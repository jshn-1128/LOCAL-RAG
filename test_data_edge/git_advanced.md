# Advanced Git Techniques

## Interactive Rebase
```bash
git rebase -i HEAD~3
```
Allows squashing, reordering, and editing commits.

## Cherry-pick
```bash
git cherry-pick <commit-hash>
```
Apply specific commits to current branch.

## Git Stash
```bash
git stash           # Save changes
git stash pop       # Restore changes
git stash list      # List stashes
```

## Bisect
```bash
git bisect start
git bisect bad
git bisect good <commit>
```
