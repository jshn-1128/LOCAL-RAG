# Git Workflows and Best Practices

Advanced Git workflows for team collaboration.

## Common Git Workflows

### Git Flow
A strict branching model with specific branch types:

- **main**: Production-ready code
- **develop**: Integration branch
- **feature/***: New features (branched from develop)
- **release/***: Release preparation
- **hotfix/***: Emergency fixes (branched from main)

### GitHub Flow
Simpler workflow for continuous delivery:
1. Create branch from main
2. Make changes and commit
3. Open pull request
4. Review and discuss
5. Merge to main
6. Deploy

### GitLab Flow
Environment-based branching:
- **main**: Latest code
- **production**: Deployed code
- **pre-production**: Staging environment

## Pull Request Best Practices

- Keep PRs small and focused
- Write descriptive titles and descriptions
- Link related issues
- Add tests for changes
- Request reviews from relevant team members
- Squash commits before merging

## Handling Merge Conflicts

```bash
# When pulling causes conflicts
git pull origin main
# Resolve conflicts in files, then:
git add resolved-file.py
git commit -m "Resolve merge conflict"

# Alternative: rebase approach
git fetch origin
git rebase origin/main
# Resolve conflicts, then:
git rebase --continue
```

## Git Hooks

Git hooks are scripts that run automatically before/after Git events:
- **pre-commit**: Lint/stage files before commit
- **pre-push**: Run tests before push
- **post-merge**: Install dependencies after merge

## Git Bisect

Find which commit introduced a bug:

```bash
git bisect start
git bisect bad          # Current commit is bad
git bisect good v1.0    # Last known good version
# Git checks out middle commits; mark each:
git bisect good         # If commit is good
git bisect bad          # If commit is bad
# Eventually git identifies the first bad commit
git bisect reset
```

## Tags and Releases

```bash
# Create annotated tag
git tag -a v1.0.0 -m "Release v1.0.0"

# Push tags to remote
git push origin --tags

# List tags
git tag -l "v1.*"
```

## Git Configuration

```bash
# Global config
git config --global user.name "Your Name"
git config --global user.email "email@example.com"
git config --global core.editor "code --wait"
git config --global init.defaultBranch main

# Aliases
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.st status
git config --global alias.lg "log --oneline --graph --all"
```
