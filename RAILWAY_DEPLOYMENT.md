# Railway Deployment Guide

This guide walks you through deploying your Knowledge Management Backend to Railway with PostgreSQL.

## Prerequisites

- GitHub repository with your code (already done ✅)
- Railway account ([railway.app](https://railway.app))
- PostgreSQL database service on Railway (already deployed ✅)

## Step 1: Create a New Project on Railway

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository: `jedidiahhorne/knowledge-management-backend`
5. Railway will automatically detect your `Dockerfile` and start building

## Step 2: Connect Your PostgreSQL Database

Since you've already deployed PostgreSQL on Railway:

1. In your Railway project, you should see your PostgreSQL service
2. Click on the PostgreSQL service
3. Go to the **"Variables"** tab
4. Find the `DATABASE_URL` variable - this is your connection string
5. Copy this value (you'll need it in the next step)

**Note:** Railway automatically provides a `DATABASE_URL` environment variable. If your PostgreSQL service is in the same project as your backend service, Railway will automatically share the `DATABASE_URL` variable.

## Step 3: Configure Environment Variables (Secrets)

1. In your Railway project, click on your **backend service** (the one deploying from GitHub)
2. Go to the **"Variables"** tab
3. Click **"New Variable"** to add each required variable

### Required Environment Variables

Add these variables one by one:

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `DATABASE_URL` | (Auto-provided) | PostgreSQL connection string from Railway |
| `ENVIRONMENT` | `production` | Set to production mode |
| `DEBUG` | `false` | Disable debug mode |
| `SECRET_KEY` | (Generate one) | JWT secret key (see below) |
| `CORS_ORIGINS` | `https://your-frontend.com` | Your frontend URL(s), comma-separated |
| `API_V1_PREFIX` | `/api/v1` | API prefix (default) |
| `PROJECT_NAME` | `Knowledge Management API` | Project name (optional) |

### Optional Environment Variables

| Variable Name | Default Value | Description |
|--------------|---------------|-------------|
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT access token expiration |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | JWT refresh token expiration |
| `UPLOAD_DIR` | `./uploads` | Directory for file uploads |
| `MAX_FILE_SIZE` | `10485760` | Max file size in bytes (10 MB) |

### Generating a Secure SECRET_KEY

**Option 1: Using Python (Recommended)**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Option 2: Using OpenSSL**
```bash
openssl rand -hex 32
```

**Option 3: Online Generator**
- Use a secure random string generator
- Minimum 32 characters recommended

Copy the generated key and paste it as the value for `SECRET_KEY` in Railway.

## Step 4: Setting Up Variables in Railway

### Method 1: Using Railway Dashboard (Easiest)

1. Click on your backend service
2. Go to **"Variables"** tab
3. Click **"New Variable"**
4. Enter the variable name (e.g., `SECRET_KEY`)
5. Enter the value
6. Click **"Add"**
7. Repeat for all variables

### Method 2: Using Railway CLI

1. Install Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

2. Login:
   ```bash
   railway login
   ```

3. Link your project:
   ```bash
   railway link
   ```

4. Set variables:
   ```bash
   railway variables set SECRET_KEY="your-secret-key-here"
   railway variables set ENVIRONMENT="production"
   railway variables set DEBUG="false"
   railway variables set CORS_ORIGINS="https://your-frontend.com"
   ```

### Important Notes About DATABASE_URL

- **If PostgreSQL is in the same Railway project:** Railway automatically shares `DATABASE_URL` - you don't need to set it manually
- **If PostgreSQL is in a different project:** You'll need to manually copy the `DATABASE_URL` from the PostgreSQL service and add it to your backend service variables

## Step 5: Verify Database Connection

Railway's `DATABASE_URL` format looks like:
```
postgresql://postgres:password@hostname:5432/railway
```

Your application is already configured to handle this format. The connection will work automatically once `DATABASE_URL` is set.

## Step 6: Deploy

Railway will automatically:
1. Build your Docker image
2. Deploy your service
3. Run database migrations (via `init_db()` in `app/main.py`)

### Manual Deploy

If you need to trigger a manual deployment:
1. Go to your service
2. Click **"Deploy"** → **"Redeploy"**

### Automatic Deployments

Railway automatically deploys on every push to your main branch. To disable:
1. Go to service settings
2. Toggle off "Auto Deploy"

## Step 7: Get Your Application URL

1. After deployment completes, Railway will provide a URL
2. It looks like: `https://your-app-name.up.railway.app`
3. Your API will be available at:
   - API Base: `https://your-app-name.up.railway.app/api/v1`
   - API Docs: `https://your-app-name.up.railway.app/docs`
   - Health Check: `https://your-app-name.up.railway.app/health`

## Step 8: Verify Deployment

1. **Check Health:**
   ```bash
   curl https://your-app-name.up.railway.app/health
   ```
   Should return: `{"status":"healthy"}`

2. **Check API Docs:**
   - Visit `https://your-app-name.up.railway.app/docs`
   - You should see the Swagger UI

3. **Test Registration:**
   ```bash
   curl -X POST https://your-app-name.up.railway.app/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "username": "testuser",
       "password": "testpassword123"
     }'
   ```

## Step 9: Custom Domain (Optional)

1. Go to your service → **"Settings"** → **"Networking"**
2. Click **"Generate Domain"** or **"Custom Domain"**
3. Add your domain and configure DNS as instructed

## Monitoring and Logs

### View Logs

1. Click on your service in Railway
2. Go to **"Deployments"** tab
3. Click on a deployment to see logs
4. Or use **"View Logs"** for real-time logs

### Common Issues

**Database Connection Errors:**
- Verify `DATABASE_URL` is set correctly
- Check that PostgreSQL service is running
- Ensure both services are in the same project (for auto-sharing)

**Build Failures:**
- Check build logs in Railway
- Verify `Dockerfile` is correct
- Ensure all dependencies are in `requirements.txt`

**Application Errors:**
- Check application logs
- Verify all environment variables are set
- Test database connection separately

## Environment Variables Summary

Here's a complete list of variables you should set:

```env
# Required
DATABASE_URL=<auto-provided-by-railway>
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generate-secure-random-key>
CORS_ORIGINS=https://your-frontend.com

# Optional (with defaults)
API_V1_PREFIX=/api/v1
PROJECT_NAME=Knowledge Management API
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
MAX_FILE_SIZE=10485760

# S3/MinIO Storage (for file uploads)
USE_S3_STORAGE=true
S3_ENDPOINT_URL=<your-minio-endpoint-url>
# MinIO credentials (copy ROOT_USER/ROOT_PASSWORD from MinIO service variables)
MINIO_ROOT_USER=<from-minio-service-ROOT_USER>
MINIO_ROOT_PASSWORD=<from-minio-service-ROOT_PASSWORD>
# Alternative: Use S3_ACCESS_KEY_ID and S3_SECRET_ACCESS_KEY for AWS S3
S3_BUCKET_NAME=files
S3_REGION=us-east-1
S3_USE_SSL=true
S3_VERIFY_SSL=true
```

## S3/MinIO Storage Configuration

The application supports S3-compatible storage (including MinIO) for file uploads. This is recommended for production deployments.

### Setting Up MinIO on Railway

1. **Add MinIO Service:**
   - In your Railway project, click **"New"** → **"Database"** → **"Add MinIO"**
   - Railway will provision a MinIO instance

2. **Get MinIO Credentials:**
   - Click on your MinIO service
   - Go to **"Variables"** tab
   - Railway MinIO provides these variables:
     - `ROOT_USER` → MinIO root username
     - `ROOT_PASSWORD` → MinIO root password
     - Check **"Networking"** tab for the public endpoint URL

3. **Configure Backend Service:**
   - Go to your backend service → **"Variables"** tab
   - Add these environment variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `USE_S3_STORAGE` | `true` | Enable S3/MinIO storage |
| `S3_ENDPOINT_URL` | `<from-minio-networking>` | MinIO endpoint URL from Networking tab |
| `MINIO_ROOT_USER` | `<from-minio-service>` | MinIO root user (copy from MinIO service `ROOT_USER` variable) |
| `MINIO_ROOT_PASSWORD` | `<from-minio-service>` | MinIO root password (copy from MinIO service `ROOT_PASSWORD` variable) |
| `S3_BUCKET_NAME` | `files` | Bucket name (use the bucket you created, default is "files") |
| `S3_REGION` | `us-east-1` | Region (not used by MinIO but required) |
| `S3_USE_SSL` | `true` | Use SSL for connections |
| `S3_VERIFY_SSL` | `true` | Verify SSL certificates (set to `false` for self-signed) |

**Note:** 
- Copy `ROOT_USER` from MinIO service variables → set as `MINIO_ROOT_USER` in backend service
- Copy `ROOT_PASSWORD` from MinIO service variables → set as `MINIO_ROOT_PASSWORD` in backend service
- The application supports both `MINIO_ROOT_USER`/`MINIO_ROOT_PASSWORD` (for MinIO) and `S3_ACCESS_KEY_ID`/`S3_SECRET_ACCESS_KEY` (for AWS S3). MinIO variables will be used automatically if `S3_ACCESS_KEY_ID` is not set.

### MinIO Endpoint URL Format

Railway MinIO endpoints typically look like:
- `https://minio-production.up.railway.app`
- Or check your MinIO service's **"Networking"** tab for the public URL

### Creating the Bucket

You can create the bucket manually in Railway's MinIO service, or the application will automatically create it if it doesn't exist:

**Manual Creation:**
1. In Railway, go to your MinIO service
2. Click on the service to access the MinIO web interface
3. Login with `ROOT_USER` and `ROOT_PASSWORD` from the service variables
4. Create a bucket named `files` (or whatever you set in `S3_BUCKET_NAME`)

**Automatic Creation:**
- The application will automatically create the bucket on first use if it doesn't exist

### Local Storage (Development)

For local development, you can use local storage by:
- Setting `USE_S3_STORAGE=false` (or omitting it)
- Files will be stored in `./uploads` directory

### File Download

When using S3 storage:
- Download endpoints return presigned URLs (valid for 1 hour)
- Files are served directly from MinIO/S3
- No files are stored in the application container

## Updating Your Deployment

1. Make changes to your code
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your changes"
   git push
   ```
3. Railway automatically detects the push and redeploys
4. Monitor the deployment in Railway dashboard

## Database Migrations

**✅ Migrations are automatically run on deployment!**

The application uses Alembic for database migrations. When the container starts:

1. **Migrations run automatically** via `scripts/start.sh` before the app starts
2. This ensures all database tables are created/updated on every deployment
3. No manual intervention needed - migrations happen automatically

### How It Works

- The Dockerfile runs `scripts/start.sh` on container startup
- The startup script runs `alembic upgrade head` to apply all pending migrations
- Then it starts the FastAPI application

### Manual Migration Commands (if needed)

If you need to run migrations manually:

```bash
# Connect to Railway service shell
railway shell

# Or using Railway CLI
railway run alembic upgrade head

# Create a new migration (after model changes)
railway run alembic revision --autogenerate -m "Description of changes"
```

### Creating New Migrations

When you modify database models:

1. Make your model changes
2. Create a new migration:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```
3. Review the generated migration file
4. Commit and push - Railway will automatically run it on deployment

## File Storage Considerations

**Current Setup:** Files are stored in `./uploads` directory inside the container.

**Limitations:**
- Files are lost when container is redeployed
- Not suitable for multiple instances

**Recommended for Production:**
- Use cloud storage (S3, Cloudflare R2, etc.)
- Or use Railway's volume mounts (if available)

## Cost Estimation

Railway pricing:
- **Free tier:** $5 credit/month
- **Hobby plan:** Pay-as-you-go (~$5-20/month for small apps)
- **Pro plan:** $20/month + usage

Your setup (backend + PostgreSQL) should fit within the free tier for development/testing.

## Support

- Railway Docs: [docs.railway.app](https://docs.railway.app)
- Railway Discord: [discord.gg/railway](https://discord.gg/railway)
- Check application logs for debugging

## Quick Reference

**Service URL:** `https://your-app-name.up.railway.app`  
**API Docs:** `https://your-app-name.up.railway.app/docs`  
**Health Check:** `https://your-app-name.up.railway.app/health`  
**API Base:** `https://your-app-name.up.railway.app/api/v1`

