# Git Commit Guide

After reorganization, you should commit these changes to Git. Here's how:

## Step 1: Check Status

```bash
git status
```

You'll see many moved files and new documentation.

## Step 2: Stage All Changes

```bash
git add .
```

Or stage specific directories:

```bash
git add README.md
git add QUICKSTART.md
git add requirements.txt
git add .gitignore
git add LICENSE
git add docs/
git add app/
git add data/
git add models/
git add notebooks/
git add results/
git add scripts/
```

## Step 3: Commit Changes

```bash
git commit -m "docs: Complete repository reorganization

- Reorganized entire project structure with clear directories
- Created comprehensive English documentation (README, guides, API docs)
- Moved all models to models/trained_models/
- Moved all scalers to models/scalers/
- Moved all datasets to data/raw/
- Moved notebooks to notebooks/
- Moved visualizations to results/visualizations/
- Added QUICKSTART guide
- Added technical documentation in docs/
- Added requirements.txt
- Added .gitignore
- Added LICENSE (MIT)
- Project is now production-ready and follows best practices"
```

## Step 4: Push to GitHub

```bash
git push origin main
```

Or if you're on a different branch:

```bash
git push origin <branch-name>
```

## Alternative: Commit in Stages

If you prefer smaller commits:

### Commit 1: Structure
```bash
git add app/ data/ models/ notebooks/ results/ scripts/
git commit -m "refactor: Reorganize project structure with clear directories"
git push
```

### Commit 2: Documentation
```bash
git add README.md QUICKSTART.md docs/ LICENSE
git commit -m "docs: Add comprehensive documentation in English"
git push
```

### Commit 3: Configuration
```bash
git add .gitignore requirements.txt
git commit -m "chore: Add .gitignore and requirements.txt"
git push
```

## Verify Changes on GitHub

After pushing, check your GitHub repository:
1. Visit https://github.com/Razitaa/CNN---DEEPL
2. Verify new structure is visible
3. Check README.md renders correctly
4. Verify all files are in correct locations

## Important Notes

### Large Files Warning

If you get errors about large files:

```bash
# See which files are large
git ls-files -s | sort -k5,5rn | head -10

# Remove large files from git (but keep locally)
git rm --cached path/to/large/file.keras
echo "*.keras" >> .gitignore
git add .gitignore
git commit -m "chore: Ignore large model files"
```

### If You Need Git LFS

For large model files, consider Git LFS:

```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.keras"
git lfs track "*.h5"
git add .gitattributes
git commit -m "chore: Add Git LFS tracking"

# Now add and commit normally
git add models/
git commit -m "feat: Add trained models with Git LFS"
git push
```

## Rollback (If Needed)

If you need to undo:

```bash
# Before push
git reset --soft HEAD~1   # Undo commit, keep changes
git reset --hard HEAD~1   # Undo commit, discard changes

# After push (use carefully!)
git revert HEAD
git push
```

## Summary Checklist

- [ ] `git status` - Check what changed
- [ ] `git add .` - Stage all changes
- [ ] `git commit -m "..."` - Commit with good message
- [ ] `git push` - Push to GitHub
- [ ] Verify on GitHub website
- [ ] Check README renders correctly
- [ ] Test clone on different machine (optional)

## Commit Message Format

Use conventional commits:

```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code restructuring
- `chore`: Maintenance tasks
- `test`: Adding tests
- `style`: Code formatting

Example:
```bash
git commit -m "docs: Add comprehensive English documentation

- Added detailed README with project overview
- Added QUICKSTART guide for quick setup
- Added technical documentation in docs/ folder
- All documentation follows best practices
- Ready for collaboration"
```

---

Good luck with your reorganized repository! 🚀
