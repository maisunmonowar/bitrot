# Contributing Guidelines

Welcome to the project! To ensure a smooth collaboration for both human developers and AI agents, please adhere strictly to the following guidelines.

## 1. Branching & Repository Strategy

- **Branch Naming:** Strictly use the format `issue%d` (e.g., `issue12`). Do not use custom names.
- **Base Branch:** Default to branching off `dev`. You should always branch from `dev` unless you are working on a stacked PR.
- **Stacked PRs:** Utilize stacked PRs as much as possible. For dependent bug fixes, branch off the relevant `issue%d` feature branch.
- **Branch Roles & Environments:**
  - `dev` Branch: We treat the `dev` branch as the primary production-like environment. Version numbering upgrades are only to be done in the `dev` branch.
  - `main` Branch: We treat the `main` branch as the 'last known bug-free / running prod code'.
- **Testing & Merging Flow:** Do as much testing as possible in local mode or in staging. Once testing is done, the PR merges it to `dev`. After the `dev` branch is running for a few days without bugs, the operations team will merge it to the `main` branch. (If we discover any surprise bugs, the operation team changes to the `main` branch immediately).

## 2. Issue & Pull Request Management

- **Issue Scope:** Keep descriptions and probable solutions short and focused.
- **Granularity:** One bug, one branch. If an issue is large, break it down into smaller, atomic issues.
- **Pull Requests:** Keep code diffs minimal.
- **Merge Policy:** We expect PR approval in the form of 'squash and merge' to keep our `dev` branch history clean and linear. The squash and merge PR policy strictly applies.

- **PR Guidance:** For PRs, try to add a flowchart/graph or short code snippets to make the change easy to understand — do not write a novel; Ain't nobody got time for that.

## 3. Commit Guidelines

- **Contextual Commits:** Your commits should be as on-topic as possible. Example: if your commit says 'Fix a logic bug', avoid including file changes to `README.md`.
- **Documentation Commits:** Try to update the docstrings and `README.md` in a single commit.
- **Cleanup Commits:** Once the PR is in draft or near draft, delete unnecessary inline comments in a single commit. Clearly state the commit task (e.g., "ready for PR. Delete discussion inline comments + typos").

## 4. Code Editing & Comment Rules

- **Active Branch Work:** In an active `issue%d` branch, never delete existing comments—only append new clarifying comments.
- **Attribution:** Sign your name/handle next to any inline code comment you add. Although `git blame` can be used, this provides a faster way to trace the development process.
- **Cleanup:** Before final PR approval/merge, clean up and delete temporary or irrelevant inline comments.

## 5. Documentation & Notes Management

- **Local Notes:** Write detailed planning, context, notes, and test plans to `changelogs/issue%d.md`. *(Note: Keep this file local and do not commit it to Git).*
- **TODO Tracker:** Any leftover tasks or future notes must be recorded in `todo.md` with sufficient context. Once a git issue has been opened based on a todo, link the git issue number in this file.
- **Pre-PR Sync:** Ensure `todo.md`, `README.md`, and other documentation are updated and in sync before creating a PR.
