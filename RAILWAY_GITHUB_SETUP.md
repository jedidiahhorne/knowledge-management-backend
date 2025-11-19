# Connecting GitHub to Railway

If your GitHub repository doesn't appear in Railway, you need to authorize Railway to access your GitHub account.

## Step 1: Authorize Railway to Access GitHub

1. **Go to Railway Settings:**
   - Visit [railway.app](https://railway.app)
   - Click on your profile icon (top right)
   - Select **"Account Settings"** or **"Settings"**

2. **Connect GitHub:**
   - Look for **"Connections"** or **"Integrations"** section
   - Find **"GitHub"** in the list
   - Click **"Connect"** or **"Authorize"**

3. **Authorize on GitHub:**
   - You'll be redirected to GitHub
   - GitHub will ask you to authorize Railway
   - You can choose to:
     - **Authorize all repositories** (easiest)
     - **Select specific repositories** (more secure)
   - Click **"Authorize railway"** or **"Install"**

4. **Verify Connection:**
   - Return to Railway
   - You should see GitHub listed as "Connected" in your connections

## Step 2: Add Repository to Railway

After authorizing:

1. **In your Railway project:**
   - Click **"+"** or **"New"**
   - Select **"GitHub Repo"**
   - Your repositories should now appear
   - Select `jedidiahhorne/knowledge-management-backend`

## Alternative: Direct Repository URL

If you still don't see the repository:

1. **In Railway project:**
   - Click **"New"** → **"Empty Service"**
   - Click on the new service
   - Go to **"Settings"** tab
   - Under **"Source"**, look for **"Connect GitHub Repo"** or **"Repository"**
   - Enter: `jedidiahhorne/knowledge-management-backend`
   - Or use the full URL: `https://github.com/jedidiahhorne/knowledge-management-backend`

## Troubleshooting

### Repository Still Not Showing

1. **Check GitHub Organization Settings:**
   - If the repo is in an organization, the org owner may need to approve Railway
   - Go to GitHub → Organization Settings → Third-party access
   - Approve Railway if needed

2. **Re-authorize Railway:**
   - In Railway Settings → Connections
   - Disconnect GitHub
   - Reconnect and authorize again

3. **Check Repository Visibility:**
   - Make sure the repository is not archived
   - If it's private, ensure Railway has access to private repos

4. **Use Railway CLI:**
   ```bash
   railway login
   railway link
   # Then manually specify the repo
   ```

### Verify GitHub Connection

To check if Railway is connected:

1. Go to Railway → Settings → Connections
2. You should see GitHub with a green checkmark or "Connected" status
3. If not, click "Connect" to set it up

## Quick Checklist

- [ ] Railway account created
- [ ] GitHub account connected in Railway settings
- [ ] Repository is not archived
- [ ] Repository visibility allows Railway access (if private)
- [ ] Organization permissions granted (if applicable)

