# 🚀 Supabase Quick Start

Get Kinemotion database running in 5 minutes.

## TL;DR - Three Commands

```bash
# 1. Configure environment
./scripts/setup-supabase-local.sh

# 2. Setup environment variables
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="sb_anon_your-key"

# 3. View schema and run in Supabase
./scripts/supabasedb/setup-supabase-database.sh
# Then copy SQL into Supabase Dashboard
```

## Step-by-Step

### 1. Create Supabase Project

1. Go to https://supabase.com and sign up (free)
1. Create a new project
1. Note your **Project URL** and **Anon Key** from Settings > API

Example:

```
Project URL: https://abcd1234.supabase.co
Anon Key: sb_anon_xyz789...
```

### 2. Run Local Setup

```bash
cd kinemotion
./scripts/setup-supabase-local.sh
```

This creates `.env` files with your configuration.

### 3. Create Database Schema

#### Option A: Using Script (Easy)

```bash
export SUPABASE_URL="https://abcd1234.supabase.co"
export SUPABASE_KEY="sb_anon_xyz789..."

./scripts/supabasedb/setup-supabase-database.sh
```

Copy the displayed SQL.

#### Option B: Manual (Fastest for First Time)

1. Go to: https://supabase.com/dashboard/project/YOUR_PROJECT_ID/sql
1. Click "New Query"
1. Paste this SQL:

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

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_analysis_sessions_user_id ON analysis_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_sessions_created_at ON analysis_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_coach_feedback_analysis_session_id ON coach_feedback(analysis_session_id);
CREATE INDEX IF NOT EXISTS idx_coach_feedback_coach_user_id ON coach_feedback(coach_user_id);

-- Enable RLS
ALTER TABLE analysis_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE coach_feedback ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY IF NOT EXISTS "users_can_read_own_sessions" ON analysis_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "users_can_create_own_sessions" ON analysis_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "coaches_can_read_feedback" ON coach_feedback
    FOR SELECT
    USING (
        auth.uid() = coach_user_id OR
        auth.uid() IN (SELECT user_id FROM analysis_sessions WHERE id = coach_feedback.analysis_session_id)
    );

CREATE POLICY IF NOT EXISTS "coaches_can_create_feedback" ON coach_feedback
    FOR INSERT WITH CHECK (auth.uid() = coach_user_id);

CREATE POLICY IF NOT EXISTS "coaches_can_update_own_feedback" ON coach_feedback
    FOR UPDATE
    USING (auth.uid() = coach_user_id)
    WITH CHECK (auth.uid() = coach_user_id);
```

4. Click "Run"

### 4. Verify Setup

In Supabase SQL Editor, run:

```sql
-- Should show: analysis_sessions, coach_feedback
SELECT tablename FROM pg_tables WHERE schemaname='public';

-- Should show: true, true
SELECT tablename, rowsecurity FROM pg_tables
WHERE tablename IN ('analysis_sessions', 'coach_feedback');

-- Should list 5 policies
SELECT policyname FROM pg_policies;
```

### 5. Test Backend

```bash
cd backend
uv sync
uv run uvicorn kinemotion_backend.app:app --reload
```

In another terminal:

```bash
curl http://localhost:8000/api/database-status
```

Should see:

```json
{"status": "connected", "database_tables": ["analysis_sessions", "coach_feedback"]}
```

## What Just Happened?

✅ **Tables Created:**

- `analysis_sessions` - Stores video analysis results
- `coach_feedback` - Stores coach feedback on analyses

✅ **Security Enabled:**

- Row Level Security (RLS) prevents data leaks
- Users can only see their own data
- Coaches can only see their own feedback

✅ **Backend Connected:**

- Backend can now read/write to database
- Authentication via Supabase JWT tokens
- All queries respect RLS policies

## Common Issues

### "SUPABASE_URL not set"

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="sb_anon_your-key"
```

### "Database connection failed"

Check:

1. Credentials are correct
1. Supabase project is running (check dashboard)
1. Network connectivity

### "RLS policy violation"

Usually means:

- User ID doesn't match
- Policy conditions are wrong
- Check `auth.uid()` matches your user

## Environment Files

After setup, you should have:

**`backend/.env`:**

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=sb_anon_your-key
SUPABASE_ANON_KEY=sb_anon_your-key
LOG_LEVEL=INFO
JSON_LOGS=false
```

**`frontend/.env.local`:**

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=sb_anon_your-key
VITE_API_URL=http://localhost:8000
```

**Keep these files SECRET!** Add to `.gitignore` (they should already be).

## Next Steps

1. Start frontend: `cd frontend && yarn dev`
1. Open http://localhost:5173
1. Sign up with email
1. Upload a video to test
1. See results in Supabase under `analysis_sessions`

## Full Documentation

For advanced setup, production deployment, and troubleshooting:

- **Complete Guide**: `docs/development/supabase-database-setup.md`
- **Setup Scripts**: `scripts/SETUP_GUIDE.md`
- **Backend Docs**: `backend/docs/setup.md`

## Support

- 📚 Supabase Docs: https://supabase.com/docs
- 🔧 Backend Code: `backend/src/kinemotion_backend/database.py`
- 🐛 Issues: Check GitHub issues
- 💬 Questions: See main README
