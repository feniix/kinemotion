# Supabase Database Setup Guide

This guide explains how to configure the Supabase PostgreSQL database for the Kinemotion backend, including environment variables, secrets management, and schema setup.

## Overview

Kinemotion uses **Supabase** for:

- PostgreSQL database (analysis sessions, coach feedback)
- Authentication (user sign-up, login, JWT tokens)
- Row Level Security (RLS) for data privacy

The backend connects to Supabase using the Supabase Python client and environment variables.

## Prerequisites

- Supabase account (free tier available at https://supabase.com)
- Backend running locally or deployed
- Python 3.10+

## Step 1: Create or Access Your Supabase Project

### Option A: Create a New Project

1. Go to https://supabase.com/dashboard
1. Click "New Project"
1. Choose a name (e.g., "kinemotion")
1. Set a database password (store securely)
1. Select your region (us-east-1 recommended for US deployments)
1. Wait 2-3 minutes for provisioning

### Option B: Use Existing Project

If you already have a Supabase project, note your project credentials.

## Step 2: Gather Supabase Credentials

You'll need these values from your Supabase project:

1. **Go to Settings → API**:

   - **Project URL**: `https://[project-id].supabase.co`
   - **Anon Key**: Public key for client-side access (starts with `sb_anon_`)
   - **Service Role Key**: Secret key for server-side access (starts with `sb_service_role_`)

1. **Go to Settings → Database**:

   - **Postgres URL**: Connection string (for migrations if needed)

Example:

```
Project URL: https://smutfsalcbnfveqijttb.supabase.co
Anon Key: sb_anon_abc123...
Service Role Key: sb_service_role_xyz789...
```

## Step 3: Create Database Schema

Run the following SQL in your Supabase project to create the required tables:

### In Supabase Dashboard:

1. Go to **SQL Editor**
1. Create a new query
1. Paste the SQL below
1. Click "Run"

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Analysis Sessions Table
CREATE TABLE IF NOT EXISTS analysis_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    jump_type VARCHAR(50) NOT NULL CHECK (jump_type IN ('cmj', 'drop_jump')),
    quality_preset VARCHAR(20) NOT NULL CHECK (quality_preset IN ('fast', 'balanced', 'accurate')),
    original_video_url TEXT,
    debug_video_url TEXT,
    results_json_url TEXT,
    analysis_data JSONB NOT NULL,
    processing_time_s FLOAT,
    upload_id VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Coach Feedback Table
CREATE TABLE IF NOT EXISTS coach_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_session_id UUID NOT NULL REFERENCES analysis_sessions(id) ON DELETE CASCADE,
    coach_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    notes TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_analysis_sessions_user_id ON analysis_sessions(user_id);
CREATE INDEX idx_analysis_sessions_created_at ON analysis_sessions(created_at DESC);
CREATE INDEX idx_coach_feedback_analysis_session_id ON coach_feedback(analysis_session_id);
CREATE INDEX idx_coach_feedback_coach_user_id ON coach_feedback(coach_user_id);

-- Enable Row Level Security
ALTER TABLE analysis_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE coach_feedback ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only see their own analysis sessions
CREATE POLICY "users_can_read_own_sessions" ON analysis_sessions
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "users_can_create_own_sessions" ON analysis_sessions
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- RLS Policy: Coaches can read feedback for their own analyses or sessions they're coaching
CREATE POLICY "coaches_can_read_feedback" ON coach_feedback
    FOR SELECT
    USING (
        auth.uid() = coach_user_id OR
        auth.uid() IN (
            SELECT user_id FROM analysis_sessions
            WHERE id = coach_feedback.analysis_session_id
        )
    );

CREATE POLICY "coaches_can_create_feedback" ON coach_feedback
    FOR INSERT
    WITH CHECK (auth.uid() = coach_user_id);

CREATE POLICY "coaches_can_update_own_feedback" ON coach_feedback
    FOR UPDATE
    USING (auth.uid() = coach_user_id)
    WITH CHECK (auth.uid() = coach_user_id);
```

## Step 4: Local Development Setup

### Create `.env` file in backend directory:

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your Supabase credentials:

```env
# Supabase Configuration (REQUIRED for database functionality)
SUPABASE_URL=https://[your-project-id].supabase.co
SUPABASE_KEY=sb_anon_[your-anon-key]

# Or use this alternative (both work - SUPABASE_ANON_KEY is more explicit):
# SUPABASE_ANON_KEY=sb_anon_[your-anon-key]

# Optional: Service role key for migrations/admin operations
# ONLY use this on backend, NEVER expose in frontend
SUPABASE_SERVICE_ROLE_KEY=sb_service_role_[your-service-role-key]

# Optional: R2 Cloud Storage
R2_ENDPOINT=https://[your-account].r2.cloudflarestorage.com
R2_ACCESS_KEY=your_access_key
R2_SECRET_KEY=your_secret_key
R2_BUCKET_NAME=kinemotion

# Optional: CORS settings
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Note**: The Supabase Python client uses `SUPABASE_KEY` or `SUPABASE_ANON_KEY` interchangeably. For clarity, we recommend:

- Backend: `SUPABASE_KEY` (can be anon key or service role key depending on use case)
- Frontend: `SUPABASE_ANON_KEY` (always public, safe to expose)

### Install dependencies:

```bash
uv sync
```

### Run backend:

```bash
uv run uvicorn kinemotion_backend.app:app --reload
```

### Test database connection:

```bash
curl http://localhost:8000/api/database-status
```

Expected response:

```json
{
  "status": "connected",
  "supabase_url": "https://smutfsalcbnfveqijttb.supabase.co",
  "database_tables": ["analysis_sessions", "coach_feedback"]
}
```

## Step 5: Production Setup (Google Cloud)

### 5.1 Create Google Secret Manager Secrets

Store your Supabase credentials in Google Secret Manager:

```bash
# Create secrets
gcloud secrets create SUPABASE_URL \
  --replication-policy="automatic" \
  --data-file=- <<< "https://[your-project-id].supabase.co"

gcloud secrets create SUPABASE_ANON_KEY \
  --replication-policy="automatic" \
  --data-file=- <<< "sb_anon_[your-anon-key]"

gcloud secrets create SUPABASE_SERVICE_ROLE_KEY \
  --replication-policy="automatic" \
  --data-file=- <<< "sb_service_role_[your-service-role-key]"
```

### 5.2 Grant Cloud Run Service Account Access

```bash
# Get your Cloud Run service account
SERVICE_ACCOUNT="kinemotion-backend-runtime@kinemotion-backend.iam.gserviceaccount.com"

# Grant access to each secret
for SECRET in SUPABASE_URL SUPABASE_ANON_KEY SUPABASE_SERVICE_ROLE_KEY; do
  gcloud secrets add-iam-policy-binding $SECRET \
    --member=serviceAccount:${SERVICE_ACCOUNT} \
    --role=roles/secretmanager.secretAccessor
done
```

### 5.3 Update Cloud Run Deployment

The deployment workflow automatically injects these secrets. Verify in `.github/workflows/deploy-backend.yml`:

```yaml
env:
  SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
  SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
```

### 5.4 Deploy Backend

```bash
git add .
git commit -m "chore: configure Supabase database for production"
git push origin main
```

GitHub Actions will:

1. Build Docker image
1. Push to Google Container Registry
1. Deploy to Cloud Run with environment variables
1. Inject secrets from Google Secret Manager

## Environment Variables Reference

| Variable                    | Required             | Description                            | Example                                         | Notes                                                                                     |
| --------------------------- | -------------------- | -------------------------------------- | ----------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `SUPABASE_URL`              | ✅ Yes               | Project URL                            | `https://abc123.supabase.co`                    | Found in Settings > API                                                                   |
| `SUPABASE_KEY`              | ✅ Yes               | Public API key (anon or service role)  | `sb_anon_abc123...` or `sb_service_role_xyz...` | Use `SUPABASE_ANON_KEY` for client-side, `SUPABASE_KEY` with service role for server-side |
| `SUPABASE_ANON_KEY`         | ✅ Yes (alternative) | Public anon key (recommended for APIs) | `sb_anon_abc123...`                             | Safe to expose in frontend. Use this for client-side requests                             |
| `SUPABASE_SERVICE_ROLE_KEY` | ❌ No                | Secret API key (bypass RLS)            | `sb_service_role_xyz...`                        | **NEVER expose in frontend**. Use only on backend for admin operations                    |
| `CORS_ORIGINS`              | ❌ No                | Allowed origins                        | `http://localhost:5173`                         | Comma-separated list                                                                      |
| `R2_ENDPOINT`               | ❌ No                | Cloudflare R2 endpoint                 | `https://abc.r2.cloudflarestorage.com`          | For cloud video storage                                                                   |
| `R2_ACCESS_KEY`             | ❌ No                | R2 access key                          | `abc123...`                                     | Pair with `R2_SECRET_KEY`                                                                 |
| `R2_SECRET_KEY`             | ❌ No                | R2 secret key                          | `xyz789...`                                     | **NEVER expose in frontend**                                                              |
| `R2_BUCKET_NAME`            | ❌ No                | R2 bucket name                         | `kinemotion`                                    | Optional if using R2                                                                      |

## Database API Endpoints

Once configured, the backend provides these database endpoints:

### Check Database Status

```bash
GET /api/database-status
```

Response:

```json
{
  "status": "connected",
  "supabase_url": "https://...",
  "database_tables": ["analysis_sessions", "coach_feedback"]
}
```

### Create Analysis Session

```bash
POST /api/analysis/sessions
Content-Type: application/json

{
  "user_id": "uuid-here",
  "jump_type": "cmj",
  "quality_preset": "balanced",
  "analysis_data": { "jump_height_m": 0.5, ... }
}
```

### Get User Sessions

```bash
GET /api/analysis/sessions?user_id=uuid-here&limit=50
```

### Add Coach Feedback

```bash
POST /api/analysis/sessions/{session_id}/feedback
Content-Type: application/json

{
  "coach_user_id": "uuid-here",
  "notes": "Good technique",
  "rating": 4,
  "tags": ["technique", "height"]
}
```

## Troubleshooting

### Issue: "SUPABASE_URL must be set"

**Solution**: Check your `.env` file exists and contains `SUPABASE_URL`:

```bash
cat backend/.env | grep SUPABASE_URL
```

### Issue: "Invalid JWT token"

**Solution**: Verify your `SUPABASE_ANON_KEY` is correct and not expired in Supabase Settings > API.

### Issue: "Database connection failed"

**Solution**:

1. Verify Supabase project is running: https://supabase.com/dashboard
1. Check network connectivity to `[project-id].supabase.co`
1. Verify credentials are correct in `.env`

### Issue: "RLS policy violation"

**Solution**: Ensure the user making the request matches the `user_id` in the query (or use service role key for admin operations).

### Issue: "Table does not exist"

**Solution**: Run the SQL schema creation steps in Supabase SQL Editor (Step 3).

## Security Best Practices

### Environment Variables & Keys

✅ **Do's:**

- Store `.env` in `.gitignore` (never commit secrets)
- Use `SUPABASE_ANON_KEY` in frontend (it's public, designed for browser use)
- Use `SUPABASE_SERVICE_ROLE_KEY` only on backend for admin operations
- Enable RLS (Row Level Security) on all tables
- Rotate API keys if accidentally exposed
- Use different keys for development vs production

❌ **Don'ts:**

- Commit `.env` files to Git
- Use service role key in frontend code or expose in client-side bundles
- Disable RLS on sensitive tables (you'll expose all data)
- Share credentials in Slack/email/version control
- Use the same keys across environments (dev, staging, prod)

### Row Level Security (RLS) Policies

RLS acts like an implicit `WHERE` clause on every database query. Key points:

- **`auth.uid()`**: Returns the authenticated user's UUID
- **`USING` clause**: Applied to SELECT and DELETE operations
- **`WITH CHECK` clause**: Applied to INSERT and UPDATE operations
- **If RLS is enabled but no policies exist**: Data is inaccessible (default deny)
- **Use two separate clauses for UPDATE**: `USING` (what they can see) + `WITH CHECK` (what they can modify)

Example policy structure:

```sql
-- Users can read their own data
CREATE POLICY "users_read_own" ON my_table
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can update their own data
CREATE POLICY "users_update_own" ON my_table
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);
```

For more details, see [Supabase RLS Documentation](https://supabase.com/docs/guides/database/postgres/row-level-security).

## Next Steps

1. ✅ Create Supabase project
1. ✅ Gather credentials
1. ✅ Create database schema
1. ✅ Configure local `.env` file
1. ✅ Test backend connection
1. 📋 Set up frontend authentication (see Frontend Guide)
1. 📋 Deploy to production (see Deployment Guide)

## How to Check Your Implementation

### Verify RLS is Enabled

In Supabase SQL Editor, run:

```sql
-- Check which tables have RLS enabled
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('analysis_sessions', 'coach_feedback');
```

Expected output:

```
tablename            | rowsecurity
---------------------+-------------
analysis_sessions    | t (true)
coach_feedback       | t (true)
```

### Test a Policy

```sql
-- Test if authenticated user can read their own session
-- Run as authenticated user with user_id = 'test-uuid'
SELECT * FROM analysis_sessions
WHERE user_id = 'test-uuid';  -- Should work

SELECT * FROM analysis_sessions
WHERE user_id = 'other-uuid'; -- Should return 0 rows (policy blocks it)
```

### Verify Credentials Work

```bash
# Quick test from command line
curl -X GET "https://[your-project-id].supabase.co/rest/v1/analysis_sessions" \
  -H "apikey: [your-anon-key]" \
  -H "Authorization: Bearer [your-anon-key]"

# Should return 200 or 401 (depending on RLS), NOT 400 or 500
```

## Common Implementation Issues & Fixes

### Issue: "Profiles or auth.users not found in RLS policies"

**Cause**: Policies referencing tables that don't exist

**Fix**: Ensure all referenced tables are created and RLS is properly enabled on them

### Issue: "RLS policies are too strict, blocking all queries"

**Cause**: Missing policies or overly restrictive conditions

**Fix**: Check that policies exist and test with the actual user_id you're querying with

### Issue: "Service role key queries work, but anon key queries fail"

**Cause**: RLS policies not set up correctly for the `anon` role

**Fix**: Explicitly specify `TO anon` in your policies:

```sql
CREATE POLICY "public_read" ON analysis_sessions
    FOR SELECT
    TO anon, authenticated
    USING (true);  -- Public read access
```

## Additional Resources

- **Supabase Python Client Docs**: https://supabase.com/docs/reference/python/initializing
- **Supabase RLS Guide**: https://supabase.com/docs/guides/database/postgres/row-level-security
- **Supabase Dashboard**: https://supabase.com/dashboard
- **Backend Code**: `backend/src/kinemotion_backend/database.py`
- **API Routes**: `backend/src/kinemotion_backend/routes/database.py`
- **Database Models**: `backend/src/kinemotion_backend/models/database.py`

## Support

For issues or questions:

- Check Supabase logs: https://supabase.com/dashboard → Logs
- Review backend logs: `gcloud logging read "resource.type=cloud_run_revision"`
- Check your policies in Supabase: SQL Editor → Query existing policies
- See [Implementation Details](../technical/implementation-details.md)
- Consult [Supabase Status Page](https://status.supabase.com/) for service incidents
