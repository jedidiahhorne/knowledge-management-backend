# MinIO Troubleshooting Guide

## File Not Found in MinIO Interface

### Step 1: Verify File Was Actually Uploaded

1. **Check API Response:**
   - After uploading, check the API response
   - Note the `file_path` value returned
   - Example: `"file_path": "123/abc123def456.pdf"`

2. **Check Application Logs:**
   - In Railway, go to your backend service → "Deployments" → Latest deployment
   - Look for any errors during file upload
   - Check for S3/MinIO connection errors

### Step 2: Verify MinIO Configuration

1. **Check Environment Variables:**
   - Go to backend service → "Variables" tab
   - Verify these are set correctly:
     - `USE_S3_STORAGE=true`
     - `S3_ENDPOINT_URL` (should match MinIO service URL)
     - `MINIO_ROOT_USER` (from MinIO service)
     - `MINIO_ROOT_PASSWORD` (from MinIO service)
     - `S3_BUCKET_NAME=files` (or your bucket name)

2. **Verify Bucket Name:**
   - The bucket name in your backend must match the bucket in MinIO
   - Default is `files`
   - Check MinIO interface to see what buckets exist

### Step 3: Check File Path Structure

Files are stored with this structure:
```
{note_id}/{unique_id}.{extension}
```

Example:
- Note ID: `123`
- File: `document.pdf`
- Stored as: `123/abc123def456.pdf`

**In MinIO interface:**
- Look in the `files` bucket (or your configured bucket name)
- Files are organized by note ID (folders)
- Each file has a unique name

### Step 4: Verify MinIO Connection

1. **Test Connection:**
   - In Railway, go to backend service → "Shell"
   - Run:
     ```bash
     python3 -c "
     from app.core.config import settings
     from app.core.storage import get_s3_client
     print('S3_ENDPOINT_URL:', settings.S3_ENDPOINT_URL)
     print('S3_BUCKET_NAME:', settings.S3_BUCKET_NAME)
     print('USE_S3_STORAGE:', settings.USE_S3_STORAGE)
     client = get_s3_client()
     print('Connection successful!')
     "
     ```

2. **List Buckets:**
   ```bash
   python3 -c "
   from app.core.storage import get_s3_client
   client = get_s3_client()
   response = client.list_buckets()
   print('Buckets:', [b['Name'] for b in response['Buckets']])
   "
   ```

3. **List Files in Bucket:**
   ```bash
   python3 -c "
   from app.core.config import settings
   from app.core.storage import get_s3_client
   client = get_s3_client()
   response = client.list_objects_v2(Bucket=settings.S3_BUCKET_NAME)
   if 'Contents' in response:
       for obj in response['Contents']:
           print('File:', obj['Key'], 'Size:', obj['Size'])
   else:
       print('Bucket is empty')
   "
   ```

### Step 5: Common Issues

#### Issue 1: Wrong Bucket Name
**Symptom:** Files uploaded but not visible

**Fix:**
- Check `S3_BUCKET_NAME` in backend variables
- Must match the bucket name in MinIO interface
- Default is `files`

#### Issue 2: Files in Different Bucket
**Symptom:** Bucket exists but is empty

**Fix:**
- Check if files were created in a different bucket
- Application auto-creates bucket if it doesn't exist
- Verify bucket name matches exactly

#### Issue 3: Wrong Endpoint URL
**Symptom:** Connection errors in logs

**Fix:**
- Get correct endpoint from MinIO service → "Networking" tab
- Should be like: `https://minio-production.up.railway.app`
- Update `S3_ENDPOINT_URL` in backend variables

#### Issue 4: Credentials Mismatch
**Symptom:** 403 Forbidden errors

**Fix:**
- Copy `ROOT_USER` from MinIO service → set as `MINIO_ROOT_USER` in backend
- Copy `ROOT_PASSWORD` from MinIO service → set as `MINIO_ROOT_PASSWORD` in backend
- Ensure no extra spaces or characters

#### Issue 5: Files in Note ID Folders
**Symptom:** Can't find files in root of bucket

**Fix:**
- Files are stored in folders by note ID: `{note_id}/{filename}`
- In MinIO interface, navigate into the note ID folder
- Example: Click on folder `123` to see files for note ID 123

### Step 6: Verify File Upload Worked

1. **Check Database:**
   - Query the `attachments` table
   - Check the `file_path` column
   - Should show path like: `123/abc123def456.pdf`

2. **Check MinIO via API:**
   ```bash
   # In Railway shell
   python3 -c "
   from app.core.config import settings
   from app.core.storage import get_s3_client
   client = get_s3_client()
   
   # List all objects
   paginator = client.get_paginator('list_objects_v2')
   pages = paginator.paginate(Bucket=settings.S3_BUCKET_NAME)
   
   for page in pages:
       if 'Contents' in page:
           for obj in page['Contents']:
               print(f\"Key: {obj['Key']}, Size: {obj['Size']} bytes\")
   "
   ```

### Step 7: Check File Path in Database

The `file_path` stored in the database should match what's in MinIO:

```sql
-- In PostgreSQL (via Railway shell or query interface)
SELECT id, filename, file_path, note_id, created_at 
FROM attachments 
ORDER BY created_at DESC 
LIMIT 10;
```

The `file_path` column shows the S3 key (MinIO object key).

### Step 8: Manual Verification

1. **Get File Path from API:**
   - Call `GET /api/v1/attachments/{attachment_id}`
   - Note the `file_path` value

2. **Search in MinIO:**
   - Open MinIO web interface
   - Go to your bucket (`files` by default)
   - Look for a folder matching the note ID
   - Inside that folder, look for the file

### Quick Diagnostic Script

Run this in Railway shell to check everything:

```bash
python3 << 'EOF'
from app.core.config import settings
from app.core.storage import get_s3_client, ensure_s3_bucket

print("=== MinIO Configuration ===")
print(f"USE_S3_STORAGE: {settings.USE_S3_STORAGE}")
print(f"S3_ENDPOINT_URL: {settings.S3_ENDPOINT_URL}")
print(f"S3_BUCKET_NAME: {settings.S3_BUCKET_NAME}")
print(f"MINIO_ROOT_USER: {settings.MINIO_ROOT_USER[:10]}..." if settings.MINIO_ROOT_USER else "MINIO_ROOT_USER: Not set")
print(f"MINIO_ROOT_PASSWORD: {'Set' if settings.MINIO_ROOT_PASSWORD else 'Not set'}")

if settings.USE_S3_STORAGE:
    try:
        print("\n=== Testing Connection ===")
        client = get_s3_client()
        ensure_s3_bucket()
        
        print("\n=== Listing Buckets ===")
        buckets = client.list_buckets()
        for bucket in buckets['Buckets']:
            print(f"  - {bucket['Name']}")
        
        print(f"\n=== Listing Objects in '{settings.S3_BUCKET_NAME}' ===")
        response = client.list_objects_v2(Bucket=settings.S3_BUCKET_NAME, MaxKeys=20)
        if 'Contents' in response:
            for obj in response['Contents']:
                print(f"  - {obj['Key']} ({obj['Size']} bytes)")
        else:
            print("  Bucket is empty")
            
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\nS3 storage is not enabled!")
EOF
```

## Still Can't Find Files?

1. **Check if files are actually being uploaded:**
   - Look at API response after upload
   - Check database for attachment records
   - Verify no errors in logs

2. **Check bucket permissions:**
   - Ensure MinIO bucket allows read/write
   - Check if bucket exists (application creates it automatically)

3. **Verify file path format:**
   - Files are stored as: `{note_id}/{unique_filename}`
   - Example: `123/abc123def456.pdf`
   - Look in the note ID folder, not the root

4. **Check for typos:**
   - Bucket name must match exactly
   - Endpoint URL must be correct
   - No trailing slashes in endpoint URL

