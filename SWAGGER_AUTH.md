# Using Bearer Token Authentication in Swagger UI

## How to Authenticate in Swagger UI

1. **Open Swagger UI:**
   - Navigate to `http://your-api-url/docs` (or `/api/v1/docs` if using prefix)

2. **Login to Get Token:**
   - Find the `/auth/login` endpoint
   - Click "Try it out"
   - Enter your username and password
   - Click "Execute"
   - Copy the `access_token` from the response

3. **Authorize in Swagger UI:**
   - Click the **"Authorize"** button at the top right of the Swagger UI
   - In the "Value" field, enter: `Bearer <your-access-token>`
     - Example: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - Click "Authorize"
   - Click "Close"

4. **Use Protected Endpoints:**
   - Now all protected endpoints will automatically include the bearer token
   - Try any endpoint that requires authentication (e.g., `/notes`, `/tags`, etc.)

## Alternative: Using /auth/login/json

If you prefer JSON over form data:

1. Use the `/auth/login/json` endpoint instead
2. Send JSON body:
   ```json
   {
     "username": "your-username",
     "password": "your-password"
   }
   ```
3. Copy the `access_token` from response
4. Click "Authorize" and enter: `Bearer <token>`

## Troubleshooting

### Getting 401 After Login

**Problem:** You logged in and got a token, but still get 401 errors.

**Solution:**
1. Make sure you clicked the **"Authorize"** button in Swagger UI
2. Enter the token as: `Bearer <token>` (include the word "Bearer" and a space)
3. Don't just paste the token - it must be in the format `Bearer <token>`

### Token Format

The token should be entered as:
```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJ0ZXN0dXNlciIsImV4cCI6MTY5OTk5OTk5OX0.signature
```

**Important:** 
- Include the word "Bearer" (capital B)
- Include a space after "Bearer"
- Don't include quotes around the token

### Token Expiration

Access tokens expire after 30 minutes by default (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).

If your token expires:
1. Use the `/auth/refresh` endpoint with your `refresh_token`
2. Or login again to get a new token

### Testing with curl

If you want to test outside of Swagger UI:

```bash
# Login
curl -X POST "http://your-api/api/v1/auth/login/json" \
  -H "Content-Type: application/json" \
  -d '{"username": "your-username", "password": "your-password"}'

# Use the token
curl -X GET "http://your-api/api/v1/notes" \
  -H "Authorization: Bearer <your-access-token>"
```

## Security Note

- Tokens are JWT tokens signed with your `SECRET_KEY`
- Never share your tokens or commit them to version control
- Use HTTPS in production
- Tokens expire automatically for security

