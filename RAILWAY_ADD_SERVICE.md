# Adding a GitHub Repository to an Existing Railway Project

If you already have a Railway project (e.g., with PostgreSQL) and want to add your backend service, follow these steps:

## Method 1: Add Service from GitHub (Recommended)

1. **Open your Railway project:**
   - Go to [railway.app](https://railway.app)
   - Click on your existing project

2. **Add a new service:**
   - Click the **"+"** button (or **"New"** button) in your project
   - Select **"GitHub Repo"** from the dropdown menu

3. **Select your repository:**
   - Railway will show a list of your GitHub repositories
   - Find and select: `jedidiahhorne/knowledge-management-backend`
   - Click **"Deploy"**

4. **Railway will automatically:**
   - Detect your `Dockerfile`
   - Start building your service
   - Add it to your existing project

5. **Configure the service:**
   - Railway will automatically share `DATABASE_URL` if your PostgreSQL is in the same project
   - Add other environment variables as needed (see RAILWAY_DEPLOYMENT.md)

## Method 2: Using Railway CLI

1. **Install Railway CLI** (if not already installed):
   ```bash
   npm i -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Link to your existing project:**
   ```bash
   railway link
   ```
   - Select your existing project from the list

4. **Add the service:**
   ```bash
   railway add
   ```
   - Select "GitHub Repo"
   - Choose your repository

5. **Deploy:**
   ```bash
   railway up
   ```

## Method 3: Manual Service Creation

If the above methods don't work:

1. **In your Railway project:**
   - Click **"New"** → **"Empty Service"**

2. **Configure the service:**
   - Click on the new service
   - Go to **"Settings"** tab
   - Under **"Source"**, click **"Connect GitHub Repo"**
   - Select your repository
   - Railway will detect the Dockerfile and deploy

## Verifying the Connection

After adding the service:

1. **Check the service is building:**
   - You should see build logs in the "Deployments" tab
   - Wait for the build to complete

2. **Verify environment variables:**
   - Go to your backend service → **"Variables"** tab
   - Check that `DATABASE_URL` is automatically available (if PostgreSQL is in the same project)
   - Add other required variables (SECRET_KEY, ENVIRONMENT, etc.)

3. **Check the service URL:**
   - Railway will provide a URL like: `https://your-service.up.railway.app`
   - Test it: `curl https://your-service.up.railway.app/health`

## Important Notes

- **Same Project = Shared Variables:** If your PostgreSQL and backend are in the same Railway project, `DATABASE_URL` is automatically shared
- **Different Projects:** If they're in different projects, you'll need to manually copy the `DATABASE_URL` from PostgreSQL service to your backend service
- **Auto-Deploy:** Railway will automatically redeploy on every push to your main branch
- **Service Names:** You can rename services in Railway by clicking on the service name

## Troubleshooting

**Can't see "GitHub Repo" option:**
- Make sure you're logged into Railway with a GitHub account
- Check that Railway has access to your GitHub repositories (Settings → Connections)

**Build fails:**
- Check the build logs in Railway
- Verify your Dockerfile is correct
- Ensure all dependencies are in requirements.txt

**Database connection issues:**
- Verify both services are in the same project
- Check that `DATABASE_URL` is set in your backend service variables
- Ensure PostgreSQL service is running

