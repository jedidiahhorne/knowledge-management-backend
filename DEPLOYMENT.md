# Deployment Guide

This guide covers deploying the Knowledge Management Backend using Docker to various hosting platforms.

## Prerequisites

- Docker installed locally (for building/testing)
- Git repository (for deployment)
- Account on a hosting platform

## Local Docker Setup

### Build and Run Locally

```bash
# Build the Docker image
docker build -t knowledge-management-api .

# Run the container
docker run -d \
  -p 8000:8000 \
  -e SECRET_KEY=your-secret-key-here \
  -e DATABASE_URL=sqlite:///./knowledge_management.db \
  -v $(pwd)/uploads:/app/uploads \
  --name knowledge-api \
  knowledge-management-api

# Or use docker-compose
docker-compose up -d
```

### Test Locally

```bash
# Check if container is running
docker ps

# View logs
docker logs knowledge-management-api

# Test the API
curl http://localhost:8000/health
```

## Hosting Platform Recommendations

### 1. Railway (Recommended - Easiest)

**Why Railway:**
- Free tier: $5 credit/month
- Automatic deployments from Git
- Built-in PostgreSQL database
- Simple configuration
- Great for small to medium projects

**Pricing:** Free tier with $5 credit, then pay-as-you-go (~$5-20/month)

**Getting Started:**
1. Sign up at [railway.app](https://railway.app)
2. Create a new project
3. Connect your GitHub repository
4. Add environment variables (see below)
5. Deploy!

**Environment Variables for Railway:**
```
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generate-a-secure-random-key>
DATABASE_URL=<railway-provides-this-if-you-add-postgres>
CORS_ORIGINS=https://your-frontend-domain.com
UPLOAD_DIR=./uploads
```

### 2. Render

**Why Render:**
- Free tier available (with limitations)
- Automatic SSL certificates
- Easy PostgreSQL setup
- Good documentation

**Pricing:** Free tier (spins down after inactivity), then $7/month for always-on

**Getting Started:**
1. Sign up at [render.com](https://render.com)
2. Create a new "Web Service"
3. Connect your GitHub repository
4. Set build command: `docker build -t knowledge-api .`
5. Set start command: `docker run -p 8000:8000 knowledge-api`
6. Add environment variables
7. Deploy!

### 3. Fly.io

**Why Fly.io:**
- Generous free tier
- Global edge deployment
- Great for low-latency applications
- PostgreSQL available

**Pricing:** Free tier includes 3 shared-cpu VMs, then pay-as-you-go

**Getting Started:**
1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Sign up: `fly auth signup`
3. Create app: `fly launch`
4. Deploy: `fly deploy`

### 4. DigitalOcean App Platform

**Why DigitalOcean:**
- Simple pricing ($5/month minimum)
- Automatic deployments
- Managed databases available
- Good for production apps

**Pricing:** $5/month for basic app, $15/month for database

**Getting Started:**
1. Sign up at [digitalocean.com](https://digitalocean.com)
2. Create App Platform app
3. Connect GitHub repository
4. Configure environment variables
5. Deploy!

### 5. Heroku (Alternative)

**Why Heroku:**
- Well-established platform
- Easy deployment
- Add-ons available

**Pricing:** No free tier anymore, starts at $5/month

**Getting Started:**
1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Set environment variables
5. Deploy: `git push heroku main`

## Environment Variables

Create a `.env` file or set these in your hosting platform:

```env
# Environment
ENVIRONMENT=production
DEBUG=false

# Database (use PostgreSQL in production)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Security
SECRET_KEY=<generate-a-strong-random-secret-key>

# API
API_V1_PREFIX=/api/v1
PROJECT_NAME=Knowledge Management API

# CORS (update with your frontend URL)
CORS_ORIGINS=https://your-frontend.com,https://www.your-frontend.com

# File Upload
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10 MB in bytes
```

### Generating a Secure Secret Key

```python
# Run this in Python
import secrets
print(secrets.token_urlsafe(32))
```

## Database Setup

### Option 1: SQLite (Development Only)
- Works out of the box
- Not recommended for production
- File-based, no separate service needed

### Option 2: PostgreSQL (Recommended for Production)

Most hosting platforms offer managed PostgreSQL:

**Railway:**
1. Add PostgreSQL service to your project
2. Copy the `DATABASE_URL` from the service
3. Set as environment variable

**Render:**
1. Create PostgreSQL database
2. Copy connection string
3. Set as `DATABASE_URL`

**Update requirements.txt:**
Uncomment `psycopg2-binary==2.9.9` in requirements.txt

## File Storage

### Local Storage (Default)
- Files stored in `./uploads` directory
- Works for single-instance deployments
- **Note:** Files are lost if container is recreated (unless using volumes)

### Recommended: Cloud Storage
For production, consider using:
- **AWS S3** (with boto3)
- **Google Cloud Storage**
- **DigitalOcean Spaces**
- **Cloudflare R2**

This requires additional code changes to use cloud storage instead of local filesystem.

## Deployment Steps (Railway Example)

1. **Prepare your repository:**
   ```bash
   git add Dockerfile docker-compose.yml .dockerignore
   git commit -m "Add Docker configuration"
   git push
   ```

2. **Sign up and create project on Railway**

3. **Deploy from GitHub:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will detect Dockerfile automatically

4. **Add PostgreSQL (optional but recommended):**
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway provides `DATABASE_URL` automatically

5. **Set environment variables:**
   - Go to your service → Variables
   - Add all required environment variables
   - Set `SECRET_KEY` to a secure random value
   - Set `ENVIRONMENT=production`
   - Set `DEBUG=false`

6. **Deploy:**
   - Railway automatically deploys on every push
   - Or click "Deploy" manually

7. **Get your URL:**
   - Railway provides a URL like `https://your-app.railway.app`
   - Access API docs at `https://your-app.railway.app/docs`

## Health Checks

Most platforms support health checks. The application includes a `/health` endpoint that returns:
```json
{"status": "healthy"}
```

Configure your platform to use: `GET /health`

## Monitoring and Logs

### View Logs
- **Railway:** Service → Logs tab
- **Render:** Logs section in dashboard
- **Fly.io:** `fly logs`
- **Docker:** `docker logs knowledge-management-api`

### Monitoring
Consider adding:
- **Sentry** for error tracking
- **Uptime monitoring** (UptimeRobot, Pingdom)
- **Application metrics** (if needed)

## Scaling Considerations

### Horizontal Scaling
If you need multiple instances:
1. Use a shared database (PostgreSQL)
2. Use cloud storage for uploads (S3, etc.)
3. Configure load balancer on your platform
4. Ensure stateless application design

### Vertical Scaling
- Most platforms allow increasing resources (CPU/RAM)
- Monitor your usage and scale as needed

## Security Checklist

- [ ] Use strong `SECRET_KEY` (32+ characters)
- [ ] Set `DEBUG=false` in production
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure CORS with specific origins
- [ ] Use HTTPS (automatic on most platforms)
- [ ] Regularly update dependencies
- [ ] Use environment variables for secrets
- [ ] Enable database backups
- [ ] Monitor logs for suspicious activity

## Troubleshooting

### Container won't start
- Check logs: `docker logs <container-name>`
- Verify environment variables are set
- Check database connection string

### Database connection errors
- Verify `DATABASE_URL` is correct
- Ensure database is accessible from container
- Check firewall/network settings

### File upload issues
- Verify `UPLOAD_DIR` exists and is writable
- Check file size limits
- Ensure volume mounts are configured (if using local storage)

## Cost Estimates

**Small Project (Low Traffic):**
- Railway: $5-10/month
- Render: $7/month (always-on) or free (spins down)
- Fly.io: Free tier sufficient
- DigitalOcean: $5-10/month

**Medium Project (Moderate Traffic):**
- Railway: $20-50/month
- Render: $25-50/month
- Fly.io: $10-30/month
- DigitalOcean: $15-40/month

## Next Steps

1. Choose a hosting platform
2. Set up your account
3. Deploy using the platform's instructions
4. Configure environment variables
5. Test your deployment
6. Set up monitoring
7. Configure custom domain (optional)

For platform-specific help, refer to each platform's documentation.

