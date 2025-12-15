---
title: Testing Backend Authentication - Quick Reference
type: note
permalink: api/testing-backend-authentication-quick-reference
---

# Testing Backend Authentication

## Backdoor Testing (No JWT Required)

### Using curl

```bash
# Test /analyze endpoint with backdoor
curl -X POST http://localhost:8000/api/analyze \
  -H "x-test-password: your-test-password" \
  -F "file=@video.mp4" \
  -F "jump_type=cmj" \
  -F "quality=balanced"

# Test with debug video
curl -X POST http://localhost:8000/api/analyze \
  -H "x-test-password: your-test-password" \
  -F "file=@video.mp4" \
  -F "jump_type=cmj" \
  -F "quality=balanced" \
  -F "debug=true"
```

### Using Postman

1. Method: `POST`
2. URL: `http://localhost:8000/api/analyze`
3. Headers tab:
   - Add: `x-test-password: your-test-password`
4. Body tab → form-data:
   - `file` (type: File) → select video
   - `jump_type` (type: Text) → `cmj` or `drop_jump`
   - `quality` (type: Text) → `fast`, `balanced`, or `accurate`
   - `debug` (type: Text, optional) → `true` or `false`

### Setting Environment Variables

**Local development** (`.env`):
```bash
TEST_PASSWORD=my-secret-testing-password
TEST_USER_ID=test-user-00000000-0000-0000-0000-000000000000
```

**Cloud Run deployment** (via GitHub Actions or gcloud):
```bash
gcloud run services update kinemotion-backend \
  --region us-central1 \
  --set-env-vars TEST_PASSWORD=my-secret-password
```

---

## Production Testing (With JWT)

### Frontend Integration

```typescript
// 1. Get session after user logs in
const { session } = useAuth()

// 2. Use token in Authorization header
const token = session?.access_token
const response = await fetch(`${backendUrl}/api/analyze`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
})
```

### Testing with Personal JWT (Advanced)

If you need to test without frontend:

1. Log in to app via frontend
2. Open browser DevTools Console
3. Get your token:
   ```javascript
   const { data } = await supabase.auth.getSession()
   console.log(data.session.access_token)
   ```
4. Use in curl:
   ```bash
   curl -X POST http://localhost:8000/api/analyze \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -F "file=@video.mp4" \
     -F "jump_type=cmj"
   ```

---

## Verifying User ID Organization in R2

After successful upload, check R2 bucket:

**Backdoor test** → Should be in:
```
uploads/test-user-00000000-0000-0000-0000-000000000000/2025/12/15/...
```

**Authenticated user** → Should be in:
```
uploads/{user_id}/2025/12/15/...
```

Where `{user_id}` is the Supabase user UUID.

---

## Troubleshooting

### 401 Unauthorized (No backdoor)

**Error**: `Authentication required`

**Causes**:
- Missing `Authorization` header
- Invalid JWT token
- Expired token
- TEST_PASSWORD not configured

**Solution**:
- Provide valid JWT token, OR
- Set TEST_PASSWORD env var and use `x-test-password` header

### 403 Forbidden (Referer Check)

**Error**: `Direct API access not allowed. Use the web interface.`

**Causes**:
- Missing Referer header
- Referer from unauthorized origin

**Solution**:
- Use from frontend (referer set automatically), OR
- Include `x-test-password` header to bypass (if TEST_PASSWORD set)

### Files in anonymous/ folder

**Cause**: Uploading with TEST_PASSWORD but not setting TEST_USER_ID

**Solution**: Set TEST_USER_ID env var or use authenticated request

---

## Success Indicators

✅ Response includes metrics and URLs (JSON 200)
✅ Files in R2 under `uploads/{user_id}/...` not `anonymous/`
✅ Can save feedback to `/api/analysis/sessions` with same auth
✅ Logs show `user_id` in analysis started/completed entries
