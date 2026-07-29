# Git Version Control

Git is a distributed version control system created by Linus Torvalds in 2005. It tracks changes in source code during software development.

## Core Concepts

### Repository
A Git repository (repo) is a data structure that stores metadata for a set of files and directories.

### Commit
A commit is a snapshot of the repository at a specific point in time. Each commit has a unique SHA-1 hash identifier.

### Branch
Branches are pointers to specific commits. The default branch is usually called `main` or `master`.

### Staging Area
The staging area (index) is where changes are prepared before committing. Files move from working directory to staging area with `git add`, then to repository with `git commit`.

## Git Branching Strategy

### Feature Branch Workflow
1. Create a branch from `main`: `git checkout -b feature/new-feature`
2. Make changes and commit
3. Push branch and create pull request
4. Merge after review

### Common Git Commands

| Command | Purpose |
|---------|---------|
| `git init` | Initialize a new repository |
| `git clone <url>` | Clone an existing repository |
| `git add <file>` | Stage changes |
| `git commit -m "msg"` | Commit staged changes |
| `git push` | Push to remote |
| `git pull` | Pull from remote |
| `git merge <branch>` | Merge branch into current |
| `git rebase <branch>` | Reapply commits on top of another tip |

### Merge vs Rebase
- **Merge**: Creates a merge commit, preserving history
- **Rebase**: Rewrites history by moving commits to a new base

## Git vs Other VCS

Unlike centralized systems like SVN, Git is distributed: every developer has a complete copy of the repository history.
