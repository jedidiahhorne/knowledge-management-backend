# Debugging Railway Deployment - Database Tables Not Created

## Step 1: Check Railway Logs

1. Go to your Railway project dashboard
2. Click on your backend service
3. Go to **"Deployments"** tab
4. Click on the latest deployment
5. Look for:
   - "Running database migrations..." message
   - Any errors related to Alembic or database connection
   - Check if the startup script is executing

## Step 2: Verify Environment Variables

1. In Railway, go to your backend service
2. Click **"Variables"** tab
3. Verify these are set:
   - `DATABASE_URL` - Should be automatically provided if PostgreSQL is in same project
   - `ENVIRONMENT=production`
   - `DEBUG=false` (or true for more verbose logs)

## Step 3: Check Database Connection

The migration might be failing silently. Let's add better error handling.

## Step 4: Manual Migration Test

You can manually run migrations using Railway CLI or shell:

### Using Railway CLI:
```bash
railway login
railway link  # Select your project
railway run alembic upgrade head
```

### Using Railway Shell:
1. In Railway dashboard → Your service → Click "..." menu
2. Select "Shell" or "Open Shell"
3. Run:
   ```bash
   alembic upgrade head
   ```

## Step 5: Check Migration Status

In Railway shell, check if migrations have been applied:
```bash
alembic current
alembic history
```

## Common Issues

### Issue 1: DATABASE_URL Not Set
- **Symptom:** Migrations fail with connection error
- **Fix:** Ensure PostgreSQL service is in the same Railway project, or manually set DATABASE_URL

### Issue 2: Startup Script Not Executing
- **Symptom:** No "Running database migrations..." in logs
- **Fix:** Check Dockerfile CMD instruction

### Issue 3: Permissions Issue
- **Symptom:** Script can't execute
- **Fix:** Ensure script has execute permissions (chmod +x)

### Issue 4: Migration Already Applied
- **Symptom:** Tables exist but migration thinks it's already done
- **Fix:** Check `alembic_version` table in database

## Quick Diagnostic Commands

Run these in Railway shell:

```bash
# Check if DATABASE_URL is set
echo $DATABASE_URL

# Check if Alembic can connect
alembic current

# Try running migrations manually
alembic upgrade head

# Check what tables exist
psql $DATABASE_URL -c "\dt"
```

