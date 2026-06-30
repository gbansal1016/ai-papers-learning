---
name: git-approval-required
description: Require explicit user confirmation before running any git commands
---

# Git Command Approval Policy

## Tool Restrictions

- **Git commands**: Always ask for explicit permission before executing any `git add`, `git commit`, `git push`, `git pull`, `git reset`, or other git operations.
- Do not automatically run git commands, even if requested in a natural way like "commit changes" or "push to origin".
- Present the git command that will be executed and wait for user approval before proceeding.

## Workflow

1. When user requests a git operation, show the exact command(s) that will run
2. Ask for explicit confirmation (e.g., "Should I proceed with: `git add ... && git commit ...`?")
3. Only execute after user confirms

This ensures git operations are always intentional and reviewed before execution.
