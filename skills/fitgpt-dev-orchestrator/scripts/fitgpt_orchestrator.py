#!/usr/bin/env python3
"""FitGPT development orchestrator helper for safe, repeatable local workflows."""

from __future__ import annotations

import argparse
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib import error as url_error
from urllib import request as url_request

LOCAL_BACKEND_URL = "http://127.0.0.1:8000"
LOCAL_FRONTEND_URL = "http://127.0.0.1:3000"
DEFAULT_PROD_BACKEND = "https://fitgpt-backend-tdiq.onrender.com"
BRANCH_PROTECTED = "dieuni"
BACKEND_TARGET = "backend-features"


def run_cmd(
    cmd: List[str],
    *,
    cwd: Optional[Path] = None,
    timeout: int = 30,
) -> Tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return 124, "", f"Timeout: {exc}"
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def git(repo: Path, args: List[str], *, timeout: int = 30) -> Tuple[int, str, str]:
    return run_cmd(["git", "-C", str(repo), *args], timeout=timeout)


def resolve_repo_root(raw_repo: Optional[str]) -> Path:
    if raw_repo:
        candidate = Path(raw_repo).expanduser().resolve()
    else:
        candidate = Path.cwd().resolve()

    if (candidate / ".git").exists():
        repo = candidate
    else:
        rc, out, _ = run_cmd(["git", "-C", str(candidate), "rev-parse", "--show-toplevel"])
        if rc != 0 or not out:
            raise RuntimeError("Could not resolve repository root. Run inside FitGPT or pass --repo.")
        repo = Path(out).resolve()

    return repo


def parse_env_file(path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    if not path.exists():
        return values

    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        values[key.strip()] = val.strip().strip('"').strip("'")
    return values


def bool_text(value: bool) -> str:
    return "yes" if value else "no"


def is_local_url(url: str) -> bool:
    u = (url or "").lower()
    return "localhost" in u or "127.0.0.1" in u


def is_render_url(url: str) -> bool:
    return ".onrender.com" in (url or "").lower()


def ref_exists(repo: Path, ref: str) -> bool:
    rc, _, _ = git(repo, ["rev-parse", "--verify", f"{ref}^{{commit}}"])
    return rc == 0


def collect_safety(repo: Path, do_fetch: bool) -> Dict[str, object]:
    safety: Dict[str, object] = {}

    rc, git_root, git_root_err = git(repo, ["rev-parse", "--show-toplevel"])
    if rc != 0:
        raise RuntimeError(f"Not a git repository: {git_root_err or 'unknown error'}")

    rc, branch, _ = git(repo, ["branch", "--show-current"])
    active_branch = branch.strip()
    detached = active_branch == ""

    _, status_porcelain, _ = git(repo, ["status", "--porcelain=v1"])
    status_lines = [line for line in status_porcelain.splitlines() if line.strip()]
    tracked_dirty = any(not line.startswith("??") for line in status_lines)
    untracked = any(line.startswith("??") for line in status_lines)

    rc, origin, origin_err = git(repo, ["remote", "get-url", "origin"])
    origin_url = origin if rc == 0 else ""

    rc, upstream, _ = git(repo, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    upstream_ref = upstream if rc == 0 else "(none)"

    fetch_attempted = False
    fetch_performed = False
    fetch_block_reason = ""
    if do_fetch:
        fetch_attempted = True
        if tracked_dirty:
            fetch_block_reason = "Tracked local changes block safe fetch."
        else:
            rc, _, err = git(repo, ["fetch", "--all", "--prune"], timeout=90)
            fetch_performed = rc == 0
            if rc != 0:
                fetch_block_reason = err or "Fetch failed"

    blockers: List[str] = []
    if detached:
        blockers.append("Repository is in detached HEAD state.")
    if not origin_url:
        blockers.append("origin remote is missing or unreadable.")
    if active_branch == BRANCH_PROTECTED:
        blockers.append("Active branch is dieuni (read-only contract).")
    if fetch_attempted and not fetch_performed:
        blockers.append(fetch_block_reason or "Fetch was blocked.")

    safety.update(
        {
            "repo_root": git_root,
            "active_branch": active_branch if active_branch else "(detached)",
            "clean": len(status_lines) == 0,
            "tracked_dirty": tracked_dirty,
            "untracked_present": untracked,
            "origin_url": origin_url if origin_url else "(missing)",
            "upstream_ref": upstream_ref,
            "git_blockers": blockers,
            "fetch_attempted": fetch_attempted,
            "fetch_performed": fetch_performed,
            "fetch_block_reason": fetch_block_reason,
        }
    )
    return safety


def safe_strategy(other_ref: str, base_only: int, other_only: int, stale: bool) -> str:
    if stale:
        return "Remote refs may be stale; refresh required before merge advice."
    if BRANCH_PROTECTED in other_ref:
        if other_only > 0 and base_only == 0:
            return "Do not merge into dieuni. Consider cherry-picking needed commits into backend-features."
        if other_only > 0 and base_only > 0:
            return "Diverged with dieuni. Use disposable integration branch or selective cherry-picks."
        return "Comparison-only branch. Keep dieuni read-only."
    if base_only == 0 and other_only > 0:
        return "Fast-forward candidate for backend-features."
    if base_only > 0 and other_only == 0:
        return "No update required; backend-features already contains this branch."
    if base_only > 0 and other_only > 0:
        return "Diverged histories; prefer cherry-picks or disposable integration branch."
    return "Already aligned."


def collect_branch_matrix(repo: Path, stale: bool) -> Dict[str, object]:
    matrix: Dict[str, object] = {"base_ref": BACKEND_TARGET, "comparisons": [], "errors": []}

    base_ref = BACKEND_TARGET
    if not ref_exists(repo, base_ref):
        if ref_exists(repo, f"origin/{BACKEND_TARGET}"):
            base_ref = f"origin/{BACKEND_TARGET}"
            matrix["errors"].append(
                f"Local {BACKEND_TARGET} not found. Using {base_ref} for read-only comparison."
            )
        else:
            matrix["errors"].append(f"Missing base branch '{BACKEND_TARGET}'.")
            matrix["base_ref"] = base_ref
            return matrix
    matrix["base_ref"] = base_ref

    rc, local_raw, _ = git(repo, ["for-each-ref", "--format=%(refname:short)", "refs/heads"])
    local_branches = local_raw.splitlines() if rc == 0 else []
    rc, remote_raw, _ = git(repo, ["for-each-ref", "--format=%(refname:short)", "refs/remotes/origin"])
    remote_branches = [b for b in remote_raw.splitlines() if b and b != "origin/HEAD"] if rc == 0 else []

    explicit: List[str] = [BACKEND_TARGET]
    if BRANCH_PROTECTED in local_branches or f"origin/{BRANCH_PROTECTED}" in remote_branches:
        explicit.append(BRANCH_PROTECTED)
    if "main" in local_branches or "origin/main" in remote_branches:
        explicit.append("main")

    all_refs = sorted(set(local_branches + remote_branches + explicit))

    for other_ref in all_refs:
        if other_ref == base_ref:
            continue
        if not ref_exists(repo, other_ref):
            continue

        rc, counts_raw, err = git(repo, ["rev-list", "--left-right", "--count", f"{base_ref}...{other_ref}"])
        if rc != 0:
            matrix["errors"].append(f"Could not compare {base_ref} vs {other_ref}: {err}")
            continue

        pieces = counts_raw.split()
        if len(pieces) != 2:
            matrix["errors"].append(f"Unexpected count format for {base_ref} vs {other_ref}: {counts_raw}")
            continue

        base_only = int(pieces[0])
        other_only = int(pieces[1])

        _, missing_raw, _ = git(repo, ["log", "--oneline", f"{base_ref}..{other_ref}", "-n", "20"])
        _, unique_raw, _ = git(repo, ["log", "--oneline", f"{other_ref}..{base_ref}", "-n", "20"])
        _, changed_files_raw, _ = git(repo, ["diff", "--name-status", f"{base_ref}...{other_ref}"])
        _, diffstat_raw, _ = git(repo, ["diff", "--stat", f"{base_ref}..{other_ref}"])

        missing_commits = [x for x in missing_raw.splitlines() if x.strip()]
        unique_commits = [x for x in unique_raw.splitlines() if x.strip()]
        changed_files = [x for x in changed_files_raw.splitlines() if x.strip()]
        diffstat = [x for x in diffstat_raw.splitlines() if x.strip()]

        matrix["comparisons"].append(
            {
                "other_ref": other_ref,
                "ahead_behind": {"commits_unique_to_base": base_only, "commits_missing_from_base": other_only},
                "missing_from_backend_features": missing_commits,
                "unique_to_backend_features": unique_commits,
                "changed_files": changed_files[:40],
                "diffstat": diffstat[:20],
                "safe_strategy": safe_strategy(other_ref, base_only, other_only, stale),
            }
        )

    return matrix


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def extract_fallback_url(api_fetch_path: Path) -> str:
    content = read_text(api_fetch_path)
    if not content:
        return ""
    match = re.search(r"REACT_APP_API_BASE_URL\s*\|\|\s*[\"']([^\"']+)[\"']", content)
    return match.group(1).strip() if match else ""


def collect_env_state(repo: Path, mode: str) -> Dict[str, object]:
    web_env_local = repo / "web" / ".env.local"
    web_env_prod = repo / "web" / ".env.production"
    backend_env = repo / "backend" / ".env"
    backend_env_example = repo / "backend" / ".env.example"
    api_fetch = repo / "web" / "src" / "api" / "apiFetch.js"
    backend_main = repo / "backend" / "app" / "main.py"

    local_env = parse_env_file(web_env_local)
    prod_env = parse_env_file(web_env_prod)
    backend_local_env = parse_env_file(backend_env)
    backend_example_env = parse_env_file(backend_env_example)

    local_url = local_env.get("REACT_APP_API_BASE_URL", "")
    prod_url = prod_env.get("REACT_APP_API_BASE_URL", "")
    fallback_url = extract_fallback_url(api_fetch)
    auth_strategy = local_env.get("REACT_APP_AUTH_STRATEGY") or prod_env.get("REACT_APP_AUTH_STRATEGY") or ""
    google_id_present = bool(
        local_env.get("REACT_APP_GOOGLE_CLIENT_ID")
        or prod_env.get("REACT_APP_GOOGLE_CLIENT_ID")
        or backend_local_env.get("GOOGLE_CLIENT_ID")
        or backend_example_env.get("GOOGLE_CLIENT_ID")
    )

    backend_main_content = read_text(backend_main)
    cors_has_localhost = ("http://localhost:3000" in backend_main_content) or (
        "http://127.0.0.1:3000" in backend_main_content
    )
    cors_has_dynamic = "CORS_ORIGINS" in backend_main_content

    risks: List[str] = []
    if local_url and not is_local_url(local_url):
        risks.append("web/.env.local API URL is not local.")
    if prod_url and is_local_url(prod_url):
        risks.append("web/.env.production points to localhost.")
    if fallback_url and prod_url and fallback_url != prod_url:
        risks.append("Source fallback URL differs from web/.env.production.")
    if not prod_url and fallback_url:
        risks.append("Production API relies on source fallback in apiFetch.js.")
    if not cors_has_localhost:
        risks.append("backend/app/main.py does not explicitly include localhost CORS origin.")
    if not cors_has_dynamic:
        risks.append("backend/app/main.py lacks dynamic CORS_ORIGINS expansion.")

    if mode != "auto":
        selected_mode = mode.upper()
    else:
        if local_url and is_local_url(local_url) and (not prod_url or is_render_url(prod_url)):
            selected_mode = "LOCAL"
        elif prod_url and is_render_url(prod_url) and not local_url:
            selected_mode = "PRODUCTION"
        elif local_url or prod_url or fallback_url:
            selected_mode = "MIXED"
        else:
            selected_mode = "UNKNOWN"

    return {
        "local_frontend_api_url": local_url or "(not set)",
        "production_frontend_api_url": prod_url or "(not set)",
        "source_fallback_url": fallback_url or "(not found)",
        "backend_cors_notes": {
            "allows_localhost_origin": cors_has_localhost,
            "supports_env_extension": cors_has_dynamic,
        },
        "auth_strategy": auth_strategy or "(not set)",
        "google_client_id_present": google_id_present,
        "selected_mode": selected_mode,
        "env_risks": risks,
    }


def probe_http(url: str, timeout: int) -> Dict[str, object]:
    started = time.time()
    try:
        req = url_request.Request(url, method="GET")
        with url_request.urlopen(req, timeout=timeout) as response:
            status = response.status
            body = response.read(200).decode("utf-8", errors="ignore")
        return {
            "url": url,
            "ok": 200 <= status < 500,
            "status": status,
            "error": "",
            "preview": body.replace("\n", " ")[:140],
            "latency_ms": int((time.time() - started) * 1000),
        }
    except url_error.HTTPError as exc:
        return {
            "url": url,
            "ok": 200 <= exc.code < 500,
            "status": exc.code,
            "error": str(exc),
            "preview": "",
            "latency_ms": int((time.time() - started) * 1000),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "url": url,
            "ok": False,
            "status": 0,
            "error": str(exc),
            "preview": "",
            "latency_ms": int((time.time() - started) * 1000),
        }


def collect_connection_checks(
    env_state: Dict[str, object],
    *,
    include_frontend: bool,
    timeout: int,
) -> Dict[str, Dict[str, object]]:
    prod_url = str(env_state.get("production_frontend_api_url", ""))
    fallback_url = str(env_state.get("source_fallback_url", ""))
    selected_mode = str(env_state.get("selected_mode", "UNKNOWN"))

    local_backend = probe_http(f"{LOCAL_BACKEND_URL}/", timeout)

    prod_probe_target = ""
    if prod_url and prod_url != "(not set)":
        prod_probe_target = prod_url.rstrip("/") + "/"
    elif fallback_url and fallback_url not in {"(not found)", "(not set)"} and is_render_url(fallback_url):
        prod_probe_target = fallback_url.rstrip("/") + "/"

    production_backend = (
        probe_http(prod_probe_target, timeout)
        if prod_probe_target
        else {
            "url": "(unknown)",
            "ok": False,
            "status": 0,
            "error": "Production backend URL is not known.",
            "preview": "",
            "latency_ms": 0,
        }
    )

    if include_frontend or selected_mode == "LOCAL":
        local_frontend = probe_http(f"{LOCAL_FRONTEND_URL}/", timeout)
    else:
        local_frontend = {
            "url": f"{LOCAL_FRONTEND_URL}/",
            "ok": False,
            "status": 0,
            "error": "Skipped (not requested).",
            "preview": "",
            "latency_ms": 0,
        }

    return {
        "local_backend_probe": local_backend,
        "production_backend_probe": production_backend,
        "local_frontend_probe": local_frontend,
    }


def production_readiness(
    repo: Path,
    env_state: Dict[str, object],
    connection: Dict[str, Dict[str, object]],
) -> Dict[str, List[str]]:
    blockers: List[str] = []
    env_gaps: List[str] = []
    improvements: List[str] = []

    prod_url = str(env_state.get("production_frontend_api_url", ""))
    fallback_url = str(env_state.get("source_fallback_url", ""))

    if prod_url in {"", "(not set)"} and fallback_url in {"", "(not found)", "(not set)"}:
        blockers.append("No production backend URL configured in env or source fallback.")
    if prod_url not in {"", "(not set)"} and is_local_url(prod_url):
        blockers.append("web/.env.production points to localhost.")

    prod_probe = connection["production_backend_probe"]
    if prod_probe["url"] != "(unknown)" and not prod_probe["ok"]:
        blockers.append(f"Production backend probe failed: {prod_probe['error'] or prod_probe['status']}.")

    if not (repo / "web" / ".env.production").exists():
        env_gaps.append("web/.env.production is missing.")
    if not (repo / "backend" / ".env.example").exists():
        env_gaps.append("backend/.env.example is missing.")
    if str(env_state.get("auth_strategy", "(not set)")) == "(not set)":
        env_gaps.append("REACT_APP_AUTH_STRATEGY is not set in frontend env.")

    cors = env_state.get("backend_cors_notes", {})
    if isinstance(cors, dict):
        if not cors.get("supports_env_extension", False):
            improvements.append("Add CORS_ORIGINS env expansion for deployed frontend origins.")
        if not cors.get("allows_localhost_origin", False):
            improvements.append("Restore localhost CORS origins for local validation.")

    if fallback_url not in {"", "(not found)", "(not set)"} and prod_url in {"", "(not set)"}:
        improvements.append("Move production URL from source fallback into web/.env.production.")

    return {
        "release_blockers": blockers,
        "env_gaps": env_gaps,
        "config_improvements": improvements,
    }


def choose_next_action(
    safety: Dict[str, object],
    branch_matrix: Dict[str, object],
    connection: Dict[str, Dict[str, object]],
    readiness: Dict[str, List[str]],
) -> str:
    blockers = list(safety.get("git_blockers", []))
    if blockers:
        return "Stop at safety gate. Resolve Git blockers before fetch, branch sync, or startup."

    if readiness["release_blockers"]:
        return "Fix production release blockers before any deploy-facing recommendation."

    if not connection["local_backend_probe"]["ok"]:
        return "Switch to debugging: inspect backend startup logs and route availability."

    comps = branch_matrix.get("comparisons", [])
    if isinstance(comps, list):
        for comp in comps:
            if not isinstance(comp, dict):
                continue
            counts = comp.get("ahead_behind", {})
            if not isinstance(counts, dict):
                continue
            unique = int(counts.get("commits_unique_to_base", 0))
            missing = int(counts.get("commits_missing_from_base", 0))
            ref = str(comp.get("other_ref", ""))
            if unique > 0 and missing > 0:
                return (
                    f"Histories diverge between {branch_matrix.get('base_ref')} and {ref}. "
                    "Use selective cherry-picks or a disposable integration branch."
                )

    return "Proceed with local development validation. Keep Git writes blocked until explicitly requested."


def print_report(
    safety: Dict[str, object],
    branch_matrix: Dict[str, object],
    env_state: Dict[str, object],
    connection: Dict[str, Dict[str, object]],
    readiness: Dict[str, List[str]],
    next_action: str,
    debug_root_cause: Optional[str] = None,
) -> None:
    print("Safety")
    print(f"- repo root: {safety['repo_root']}")
    print(f"- active branch: {safety['active_branch']}")
    print(f"- cleanliness: {'clean' if safety['clean'] else 'dirty'}")
    print(f"- origin: {safety['origin_url']}")
    print(f"- upstream state: {safety['upstream_ref']}")
    blockers = safety.get("git_blockers", [])
    if blockers:
        print("- Git blockers:")
        for item in blockers:
            print(f"  - {item}")
    else:
        print("- Git blockers: none")

    print("\nBranch Matrix")
    print(f"- {BACKEND_TARGET} vs {BRANCH_PROTECTED}:")
    target_comp = None
    main_comp = None
    others: List[Dict[str, object]] = []
    for comp in branch_matrix.get("comparisons", []):
        if not isinstance(comp, dict):
            continue
        ref = str(comp.get("other_ref", ""))
        if ref in {BRANCH_PROTECTED, f"origin/{BRANCH_PROTECTED}"}:
            target_comp = comp
        elif ref in {"main", "origin/main"}:
            main_comp = comp
        else:
            others.append(comp)

    def print_comp(comp: Optional[Dict[str, object]], label: str) -> None:
        if not comp:
            print(f"  - {label}: not available")
            return
        counts = comp["ahead_behind"]
        print(
            f"  - ahead/behind counts: unique_to_backend_features={counts['commits_unique_to_base']}, "
            f"missing_from_backend_features={counts['commits_missing_from_base']}"
        )
        print("  - missing commits:")
        missing = comp.get("missing_from_backend_features", [])
        if missing:
            for line in missing[:8]:
                print(f"    - {line}")
        else:
            print("    - none")
        print("  - changed-file summary:")
        files = comp.get("changed_files", [])
        if files:
            for line in files[:8]:
                print(f"    - {line}")
        else:
            print("    - none")
        print(f"  - recommended safe strategy: {comp['safe_strategy']}")

    print_comp(target_comp, BRANCH_PROTECTED)
    print(f"- {BACKEND_TARGET} vs main:")
    print_comp(main_comp, "main")

    print(f"- {BACKEND_TARGET} vs other branches:")
    if others:
        for comp in others[:30]:
            ref = str(comp.get("other_ref"))
            counts = comp["ahead_behind"]
            print(
                f"  - {ref}: unique_to_backend_features={counts['commits_unique_to_base']}, "
                f"missing_from_backend_features={counts['commits_missing_from_base']}"
            )
    else:
        print("  - none")

    matrix_errors = branch_matrix.get("errors", [])
    if matrix_errors:
        for err in matrix_errors:
            print(f"  - note: {err}")

    print("\nEnv State")
    print(f"- local frontend API URL: {env_state['local_frontend_api_url']}")
    print(f"- production frontend API URL: {env_state['production_frontend_api_url']}")
    print(f"- source fallback URL: {env_state['source_fallback_url']}")
    cors = env_state["backend_cors_notes"]
    print(
        "- backend frontend URL / CORS notes: "
        f"allows_localhost={bool_text(cors['allows_localhost_origin'])}, "
        f"supports_env_extension={bool_text(cors['supports_env_extension'])}"
    )
    print(f"- selected mode: {env_state['selected_mode']}")
    risks = env_state.get("env_risks", [])
    if risks:
        print("- env risks:")
        for risk in risks:
            print(f"  - {risk}")
    else:
        print("- env risks: none")

    print("\nConnection Checks")
    for key, label in [
        ("local_backend_probe", "local backend probe"),
        ("production_backend_probe", "production backend probe"),
        ("local_frontend_probe", "local frontend probe"),
    ]:
        probe = connection[key]
        ok = "pass" if probe["ok"] else "fail"
        details = probe["error"] if probe["error"] else f"status={probe['status']}"
        print(f"- {label}: {ok} ({probe['url']}) {details}")

    if debug_root_cause:
        print("\nDebug Root Cause")
        print(f"- {debug_root_cause}")

    print("\nProduction Readiness")
    blockers = readiness["release_blockers"]
    gaps = readiness["env_gaps"]
    improvements = readiness["config_improvements"]
    if blockers:
        print("- release blockers:")
        for item in blockers:
            print(f"  - {item}")
    else:
        print("- release blockers: none")
    if gaps:
        print("- env gaps:")
        for item in gaps:
            print(f"  - {item}")
    else:
        print("- env gaps: none")
    if improvements:
        print("- config improvements:")
        for item in improvements:
            print(f"  - {item}")
    else:
        print("- config improvements: none")

    print("\nNext Safe Action")
    print(f"- {next_action}")


def launch_process(
    cmd: List[str],
    *,
    cwd: Path,
    log_path: Path,
) -> subprocess.Popen:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_file = open(log_path, "a", encoding="utf-8")  # noqa: SIM115
    kwargs = {
        "cwd": str(cwd),
        "stdout": log_file,
        "stderr": subprocess.STDOUT,
    }
    if platform.system().lower().startswith("win"):
        creationflags = 0
        creationflags |= getattr(subprocess, "DETACHED_PROCESS", 0)
        creationflags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        kwargs["creationflags"] = creationflags
    else:
        kwargs["start_new_session"] = True

    return subprocess.Popen(cmd, **kwargs)  # type: ignore[arg-type]


def start_services(repo: Path, timeout: int, check_only: bool) -> Dict[str, object]:
    status: Dict[str, object] = {"started": [], "errors": []}

    if check_only:
        status["note"] = "check-only requested; startup skipped."
        return status

    scripts_dir = repo / "scripts"
    codex_dir = repo / ".codex" / "dev"
    log_dir = codex_dir / "logs"
    pid_dir = codex_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    pid_dir.mkdir(parents=True, exist_ok=True)

    backend_candidates: List[Tuple[List[str], Path]] = []
    web_candidates: List[Tuple[List[str], Path]] = []

    backend_ps1 = scripts_dir / "run-backend.ps1"
    backend_sh = scripts_dir / "run-backend.sh"
    web_ps1 = scripts_dir / "run-web.ps1"
    web_sh = scripts_dir / "run-web.sh"
    web_bat_root = repo / "run-web.bat"
    web_bat_script_dir = scripts_dir / "run-web.bat"

    is_windows = platform.system().lower().startswith("win")

    if is_windows:
        if backend_ps1.exists():
            backend_candidates.append(
                (["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(backend_ps1)], repo)
            )
        if web_ps1.exists():
            web_candidates.append(
                (["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(web_ps1)], repo)
            )
        if web_bat_script_dir.exists():
            web_candidates.append((["cmd", "/c", str(web_bat_script_dir)], repo))
        if web_bat_root.exists():
            web_candidates.append((["cmd", "/c", str(web_bat_root)], repo))
    else:
        if backend_sh.exists():
            backend_candidates.append((["bash", str(backend_sh)], repo))
        if web_sh.exists():
            web_candidates.append((["bash", str(web_sh)], repo))

    # Safe fallbacks when preferred run scripts do not exist.
    if not backend_candidates:
        py_cmd = "python" if is_windows else "python3"
        backend_candidates.append(
            (
                [
                    py_cmd,
                    "-m",
                    "uvicorn",
                    "app.main:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8000",
                    "--reload",
                ],
                repo / "backend",
            )
        )
        status["errors"].append(
            "scripts/run-backend.(ps1|sh) not found. Used uvicorn fallback."
        )
    if not web_candidates:
        npm_cmd = "npm.cmd" if is_windows else "npm"
        web_candidates.append(([npm_cmd, "start"], repo / "web"))
        status["errors"].append("scripts/run-web.(ps1|sh) not found. Used npm start fallback.")

    services = [
        ("backend", backend_candidates[0]),
        ("frontend", web_candidates[0]),
    ]

    for service_name, (cmd, cwd) in services:
        try:
            proc = launch_process(cmd, cwd=cwd, log_path=log_dir / f"{service_name}.log")
            (pid_dir / f"{service_name}.pid").write_text(str(proc.pid), encoding="utf-8")
            status["started"].append(
                {
                    "service": service_name,
                    "pid": proc.pid,
                    "command": " ".join(cmd),
                    "cwd": str(cwd),
                }
            )
        except Exception as exc:  # noqa: BLE001
            status["errors"].append(f"Failed to start {service_name}: {exc}")

    # Give process supervisor a short window before probing.
    time.sleep(min(timeout, 4))
    return status


def validate_repo_shape(repo: Path) -> List[str]:
    problems: List[str] = []
    required = ["backend", "web", "scripts"]
    for name in required:
        if not (repo / name).exists():
            problems.append(f"Missing expected path: {name}/")
    return problems


def build_report(
    *,
    repo: Path,
    mode: str,
    do_fetch: bool,
    timeout: int,
    include_frontend_probe: bool,
) -> Tuple[Dict[str, object], Dict[str, object], Dict[str, object], Dict[str, Dict[str, object]], Dict[str, List[str]], str]:
    safety = collect_safety(repo, do_fetch)
    stale = bool(do_fetch and not safety["fetch_performed"])
    branch_matrix = collect_branch_matrix(repo, stale=stale)
    env_state = collect_env_state(repo, mode)
    connection = collect_connection_checks(env_state, include_frontend=include_frontend_probe, timeout=timeout)
    readiness = production_readiness(repo, env_state, connection)
    next_action = choose_next_action(safety, branch_matrix, connection, readiness)
    return safety, branch_matrix, env_state, connection, readiness, next_action


def cmd_report(args: argparse.Namespace) -> int:
    repo = resolve_repo_root(args.repo)
    repo_shape_errors = validate_repo_shape(repo)

    safety, branch_matrix, env_state, connection, readiness, next_action = build_report(
        repo=repo,
        mode=args.mode,
        do_fetch=args.fetch,
        timeout=args.timeout,
        include_frontend_probe=args.frontend_probe,
    )

    if repo_shape_errors:
        safety.setdefault("git_blockers", [])
        for problem in repo_shape_errors:
            safety["git_blockers"].append(problem)

    print_report(safety, branch_matrix, env_state, connection, readiness, next_action)
    return 0


def cmd_start(args: argparse.Namespace) -> int:
    repo = resolve_repo_root(args.repo)
    repo_shape_errors = validate_repo_shape(repo)

    safety = collect_safety(repo, do_fetch=args.fetch)
    if repo_shape_errors:
        safety.setdefault("git_blockers", [])
        for problem in repo_shape_errors:
            safety["git_blockers"].append(problem)

    if safety.get("git_blockers"):
        branch_matrix = collect_branch_matrix(repo, stale=not bool(safety.get("fetch_performed")))
        env_state = collect_env_state(repo, args.mode)
        connection = collect_connection_checks(env_state, include_frontend=True, timeout=args.timeout)
        readiness = production_readiness(repo, env_state, connection)
        next_action = "Stop and resolve safety blockers before starting local services."
        print_report(
            safety,
            branch_matrix,
            env_state,
            connection,
            readiness,
            next_action,
            debug_root_cause=None,
        )
        return 2

    startup = start_services(repo, timeout=args.timeout, check_only=args.check_only)

    safety, branch_matrix, env_state, connection, readiness, next_action = build_report(
        repo=repo,
        mode=args.mode,
        do_fetch=False,
        timeout=args.timeout,
        include_frontend_probe=True,
    )

    debug_message = None
    if startup.get("errors"):
        debug_message = "; ".join(startup["errors"])

    print_report(
        safety,
        branch_matrix,
        env_state,
        connection,
        readiness,
        next_action,
        debug_root_cause=debug_message,
    )

    if startup.get("started"):
        print("\nStartup")
        for item in startup["started"]:
            print(
                f"- {item['service']}: pid={item['pid']} cwd={item['cwd']} cmd={item['command']}"
            )
    if startup.get("errors"):
        print("- startup notes:")
        for err in startup["errors"]:
            print(f"  - {err}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="FitGPT orchestration helper for safe repo, env, and connectivity workflows."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    report = subparsers.add_parser("report", help="Run read-only safety, branch, env, and probe report.")
    report.add_argument("--repo", type=str, default=None, help="FitGPT repository root.")
    report.add_argument("--mode", choices=["auto", "local", "production"], default="auto")
    report.add_argument("--fetch", action="store_true", help="Fetch remotes if safe.")
    report.add_argument("--timeout", type=int, default=12, help="HTTP and process probe timeout in seconds.")
    report.add_argument(
        "--frontend-probe",
        action="store_true",
        help="Probe local frontend URL in report mode.",
    )
    report.set_defaults(func=cmd_report)

    start = subparsers.add_parser(
        "start",
        help="Start detached local backend/frontend using repo scripts when available.",
    )
    start.add_argument("--repo", type=str, default=None, help="FitGPT repository root.")
    start.add_argument("--mode", choices=["auto", "local", "production"], default="auto")
    start.add_argument("--fetch", action="store_true", help="Fetch remotes if safe before startup.")
    start.add_argument("--timeout", type=int, default=120, help="Probe timeout window in seconds.")
    start.add_argument(
        "--check-only",
        action="store_true",
        help="Do not relaunch services. Only run readiness and probes.",
    )
    start.set_defaults(func=cmd_start)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
