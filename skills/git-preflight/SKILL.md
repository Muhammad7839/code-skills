---
name: git-preflight
description: Conservative Git pre-flight safety procedure used before any development work. Use when validating repository readiness, branch safety, local state cleanliness, origin sync status, and teammate branch ownership while preventing accidental overwrites, unsafe pulls, merge commits, and work on protected branches.
---

# Git Preflight Safety Checklist

## File Role
This skill defines a strict, read-first, safety-first Git pre-flight flow.
Run it before coding, editing, committing, pulling, or branch operations.

## Operating Rules
- Treat the task as a safety check, not a development task.
- Do not run `git init`.
- Do not create a new repository.
- Do not run `git commit`.
- Do not run `git push`.
- Do not run `git merge`.
- Do not switch branches automatically.
- Do not overwrite local changes.
- Do not modify project files.
- If a requested or implied action would violate these rules, stop and ask.

## Default Assumptions
- Assume the user wants the smallest safe sequence of Git inspection commands needed to confirm readiness.
- If the repository is missing, ask for the repository URL before cloning.
- If branch ownership is known, include it in final safety guidance.
- If the active branch is detached or unclear, stop and ask instead of guessing.

## Workflow

### 1. Validate Repository
Check whether current working directory is inside a Git repository.

If it is not a Git repository:
- Ask for the repository URL.
- Clone the repository.
- Enter the project directory.

After confirming repository exists:
- Verify `origin` remote is configured.
- Report origin URL plainly.
- If origin is missing or clearly wrong, stop and ask.

Recommended checks:
```bash
git rev-parse --is-inside-work-tree
git remote -v
```

### 2. Identify Current Branch
Run:
```bash
git branch
```

Identify active branch from `*`.
Explain whether it appears to be:
- mainline branch such as `main` or `master`
- feature branch
- teammate-owned branch when project context defines ownership

If HEAD is detached, or branch cannot be determined confidently, stop and ask.

### 3. Inspect Local State Before Network Operations
Run:
```bash
git status --short
git status
```

If there are modified, staged, or untracked files:
- List every affected file.
- Group them as modified, staged, or untracked.
- Stop and ask: `What would you like to do?`

Present only these choices unless user asks for more:
- keep changes
- stash changes
- discard changes

Do not fetch or pull until user has decided.

### 4. Synchronize With Origin in Safe Mode
Run this step only when working tree is clean, or user explicitly chose how local changes are handled.

Run:
```bash
git fetch origin
git pull --ff-only origin <current-branch>
```

Never replace `--ff-only` with merge or rebase flow unless user explicitly changes requirement.

If pull fails:
- Explain exact reason in plain language.
- Stop.

Possible failure explanations:
- local branch is behind and cannot fast-forward cleanly because of local state
- local and remote branches have diverged
- remote branch does not exist
- pulling would require a merge commit or another non-fast-forward action

### 5. Validate Post-Sync State
Run:
```bash
git status
```

Confirm when true:
- branch is up to date with `origin/<current-branch>`
- working tree is clean
- no staged or unstaged changes remain

Explain what `up to date` means:
- local branch tip matches remote tracking branch, so starting work now does not overwrite unseen remote commits

### 6. Add Team Safety Context
Use known ownership rules when provided by user or project context.

For FitGPT:
- If branch is `dieuni`, warn: `This is the frontend branch owned by another developer. Do not modify unless explicitly required.`
- If branch is not `dieuni`, confirm: `You are working in your own branch, safe for backend/integration work.`

If ownership rules are unknown for another repository:
- state branch ownership is not defined
- do not invent ownership

### 7. Finish and Stop
Provide concise readiness summary including:
- repository status
- current branch
- sync status
- safety confirmation

If all checks pass, end with this exact sentence:
`Environment is clean, synchronized, and safe. You can begin work.`

Then stop and wait for user’s next command.
Do not continue automatically into coding, edits, or branch changes.

## Response Pattern
Prefer short factual output in this order:
1. Repository validation result
2. Active branch and branch type
3. Local state result
4. Sync result
5. Team safety note
6. Final readiness statement

When stopping for user input:
- be explicit about why progress is blocked
- show safe options available

## Failure Handling
If any step fails, do not stop silently.

You must:
- Identify failure type.
- Explain root cause in plain language.
- Provide safe options.
- Never auto-fix.

### Common Failure Cases

#### 1. Branch Is Behind Origin
Explain:
- Remote has commits local does not have.
- Push will fail until branch is synchronized.

Safe options:
- `git pull --ff-only`
- `git pull --rebase`

Explain difference clearly:
- `git pull --ff-only` updates local history only when Git can move straight forward without rewriting commits or creating merge commit.
- `git pull --rebase` replays local commits on top of updated remote branch, rewriting local commit history while keeping linear timeline.

#### 2. Non-Fast-Forward Push Rejected
Explain:
- Local history diverged from remote branch.

Safe options:
- pull, then push
- rebase, then push

Clarify:
- rejection means Git will not overwrite remote history automatically.

#### 3. Merge Conflict Risk
Explain:
- same files changed in multiple places and Git may not combine safely without manual review.

Action:
- Stop.
- Ask user how to proceed.

#### 4. Detached HEAD
Explain:
- repository is not currently on a branch.
- new commits can become hard to find or be lost from normal branch history.

Action:
- Suggest creating a branch.

#### 5. No Remote Origin
Explain:
- repository is not linked to a GitHub remote named `origin`.

Action:
- Ask for repository URL.

## Final Safety Rule
Never execute destructive commands:
- no `git reset --hard`
- no force push

Always ask first.
