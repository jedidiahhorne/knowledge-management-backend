# Getting Your Project on GitHub

## Method 1: Using GitHub CLI (Easiest - Recommended)

If you have GitHub CLI installed:

```bash
# Authenticate (if not already done)
gh auth login

# Create repository and push
cd /Users/jed/source/knowledge-management-backend
gh repo create knowledge-management-backend --public --source=. --remote=origin --push
```

For a private repository:
```bash
gh repo create knowledge-management-backend --private --source=. --remote=origin --push
```

## Method 2: Using GitHub Web Interface (Also Easy)

1. **Create the repository on GitHub:**
   - Go to [github.com](https://github.com) and sign in
   - Click the "+" icon in the top right → "New repository"
   - Name it: `knowledge-management-backend`
   - Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
   - Click "Create repository"

2. **Push your code:**
   ```bash
   cd /Users/jed/source/knowledge-management-backend
   
   # Add the remote (replace YOUR_USERNAME with your GitHub username)
   git remote add origin https://github.com/YOUR_USERNAME/knowledge-management-backend.git
   
   # Push to GitHub
   git push -u origin main
   ```

## Method 3: Using SSH (If you have SSH keys set up)

```bash
cd /Users/jed/source/knowledge-management-backend

# Add SSH remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin git@github.com:YOUR_USERNAME/knowledge-management-backend.git

# Push to GitHub
git push -u origin main
```

## After Pushing

Once your code is on GitHub, you can:

1. **View your repository:** `https://github.com/YOUR_USERNAME/knowledge-management-backend`
2. **Deploy to Railway/Render/etc:** Connect your GitHub repo for automatic deployments
3. **Share with others:** Give them the repository URL

## Troubleshooting

### If you get "repository already exists" error:
- The repository name might be taken
- Try a different name or add your username: `YOUR_USERNAME-knowledge-management-backend`

### If authentication fails:
- For HTTPS: You may need a Personal Access Token instead of password
- Generate one at: GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
- Use the token as your password when pushing

### If you need to change the remote URL:
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/knowledge-management-backend.git
```

