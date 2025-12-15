# Kinemotion Supabase Setup Guide

Complete guide for setting up the Supabase database and environment configuration for Kinemotion.

## Overview

The setup process has three stages:

1. **Local Environment Setup** - Configure `.env` files with Supabase credentials
1. **Database Schema Setup** - Create tables and Row Level Security (RLS) policies
1. **Production Setup** (Optional) - Configure Google Cloud secrets for Cloud Run

## Prerequisites

- Supabase account (free at https://supabase.com)
- Supabase project created
- Supabase credentials (Project URL, Anon Key)
- bash or Python 3.10+ (for script execution)

## Quick Start

### 1️⃣ Local Environment Setup

```bash
./scripts/setup-supabase-local.sh
```

This creates:

- `frontend/.env.local` - Frontend Supabase configuration
- `backend/.env` - Backend Supabase configuration

**What it does:**

- Copies example environment files
- Adds Supabase URL and API keys
- Configures API endpoints

**Output:**

```
✅ Frontend environment configured
✅ Backend environment configured
```

### 2️⃣ Database Schema Setup

#### Option A: Using Bash Script (Recommended)

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="sb_anon_your-key"

./scripts/setup-supabase-database.sh
```

This displays:

- SQL schema to copy/paste into Supabase
- Manual setup instructions
- Verification checklist

#### Option B: Using Python Script

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="sb_anon_your-key"

python scripts/setup_supabase_db.py
```

This:

- Validates credentials
- Generates SQL schema
- Saves schema to `backend/supabase-schema.sql`
- Displays setup instructions

#### Option C: Manual Setup (No Scripts)

1. Go to https://supabase.com/dashboard/project/[your-project-id]/sql
1. Create a new query
1. Copy SQL from `backend/supabase-schema.sql` or the script output
1. Click "Run"

### 3️⃣ Verify Setup

After running the SQL schema, verify in Supabase SQL Editor:

```sql
-- Check tables exist
SELECT tablename FROM pg_tables
WHERE schemaname='public'
AND tablename IN ('analysis_sessions', 'coach_feedback');

-- Check RLS is enabled
SELECT tablename, rowsecurity FROM pg_tables
WHERE schemaname='public'
AND tablename IN ('analysis_sessions', 'coach_feedback');

-- Check policies exist
SELECT tablename, policyname FROM pg_policies
WHERE schemaname='public';
```

### 4️⃣ Test Backend Connection

```bash
cd backend
uv sync
uv run uvicorn kinemotion_backend.app:app --reload
```

In another terminal:

```bash
curl http://localhost:8000/api/database-status
```

Expected response:

```json
{
  "status": "connected",
  "supabase_url": "https://...",
  "database_tables": ["analysis_sessions", "coach_feedback"]
}
```

## Script Details

### `setup-supabase-local.sh`

**Purpose:** Configure local environment files

**Usage:**

```bash
./scripts/setup-supabase-local.sh
```

**Creates:**

- `frontend/.env.local`
- `backend/.env`

**Configuration:**
Edit the script to change default values:

```bash
# Line 14-15 (Frontend)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-key

# Line 28-29 (Backend)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-key
```

### `setup-supabase-database.sh`

**Purpose:** Display database schema and setup instructions

**Usage:**

```bash
./scripts/setup-supabase-database.sh
```

**Requirements:**

- `SUPABASE_URL` environment variable set
- `SUPABASE_KEY` or `SUPABASE_ANON_KEY` environment variable set

**What it does:**

1. Validates credentials
1. Displays SQL schema
1. Shows manual setup instructions
1. Provides verification checklist
1. Suggests next steps

**Options:**

- Manual copy/paste into Supabase
- Supabase CLI (`supabase db push`)
- Direct execution (coming soon)

### `setup_supabase_db.py`

**Purpose:** Python-based schema setup with validation

**Usage:**

```bash
python scripts/setup_supabase_db.py
```

**Requirements:**

- Python 3.10+
- `SUPABASE_URL` environment variable set
- `SUPABASE_KEY` or `SUPABASE_ANON_KEY` environment variable set

**What it does:**

1. Validates Supabase credentials
1. Generates SQL schema
1. Saves schema to `backend/supabase-schema.sql`
1. Displays setup instructions
1. Shows verification checklist
1. Creates environment validation report

**Advantages:**

- Colored output with status indicators
- Saves schema to file for later use
- More detailed verification instructions
- Python-based for cross-platform compatibility

### `setup-supabase-production.sh`

**Purpose:** Configure Google Cloud secrets for production

**Usage:**

```bash
./scripts/setup-supabase-production.sh
```

**What it does:**

1. Creates Google Secret Manager secrets
1. Grants Cloud Run service account access
1. Configures deployment variables

**Requires:**

- Google Cloud project with billing enabled
- `gcloud` CLI installed
- Sufficient IAM permissions

## Environment Variables

### Required (Database Connection)

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=sb_anon_your-key
```

### Alternative Names

```env
SUPABASE_ANON_KEY=sb_anon_your-key          # Alternative to SUPABASE_KEY
SUPABASE_SERVICE_ROLE_KEY=sb_service_role_... # For admin operations
```

### Frontend Specific

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=sb_anon_your-key
VITE_API_URL=http://localhost:8000
```

### Optional (Storage & CORS)

```env
R2_ENDPOINT=https://your-account.r2.cloudflarestorage.com
R2_ACCESS_KEY=your-access-key
R2_SECRET_KEY=your-secret-key
R2_BUCKET_NAME=kinemotion

CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Troubleshooting

### Script Fails: "SUPABASE_URL not set"

**Solution:**

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="sb_anon_your-key"
./scripts/setup-supabase-database.sh
```

### Database Connection Fails

**Check:**

1. SUPABASE_URL is correct format
1. SUPABASE_KEY is valid (not expired)
1. Supabase project is running (check dashboard)
1. Network connectivity to Supabase servers

### RLS Policies Don't Work

**Check:**

1. Policies were created successfully
1. RLS is actually enabled on the table
1. User is authenticated (has valid JWT token)
1. Policy conditions match your user ID

**Verify:**

```sql
-- List all policies
SELECT * FROM pg_policies WHERE schemaname='public';

-- Check specific table RLS
SELECT rowsecurity FROM pg_tables
WHERE tablename='analysis_sessions';
```

### Script Permission Denied

**Solution:**

```bash
chmod +x scripts/setup-supabase-database.sh
chmod +x scripts/setup_supabase_db.py
```

## Files Generated

After running the scripts, you'll have:

```
project-root/
├── backend/
│   ├── .env (created by setup-supabase-local.sh)
│   └── supabase-schema.sql (created by setup_supabase_db.py)
├── frontend/
│   └── .env.local (created by setup-supabase-local.sh)
└── scripts/
    ├── setup-supabase-local.sh
    ├── setup-supabase-database.sh
    ├── setup_supabase_db.py
    └── setup-supabase-production.sh
```

## Complete Setup Checklist

- [ ] Create Supabase project at https://supabase.com
- [ ] Get Project URL and Anon Key from Settings > API
- [ ] Run `./scripts/setup-supabase-local.sh`
- [ ] Set environment variables
- [ ] Run `./scripts/setup-supabase-database.sh` or `python scripts/setup_supabase_db.py`
- [ ] Execute SQL schema in Supabase Dashboard
- [ ] Verify tables and RLS policies exist
- [ ] Test backend connection with curl
- [ ] Start frontend and test login
- [ ] (Optional) Run `./scripts/setup-supabase-production.sh` for production

## Next Steps

1. **Frontend Setup**: See `frontend/README.md`
1. **Backend Setup**: See `backend/docs/setup.md`
1. **Testing**: See `docs/development/testing.md`
1. **Deployment**: See `docs/deployment/`

## Support

- **Documentation**: See `docs/development/supabase-database-setup.md`
- **Supabase Docs**: https://supabase.com/docs
- **Backend API**: `backend/src/kinemotion_backend/database.py`
- **Issues**: Check GitHub issues for similar problems

## Script Maintenance

These scripts are designed to be:

- **Idempotent** - Safe to run multiple times
- **Portable** - Work on macOS, Linux, Windows (with bash)
- **Verifiable** - Include validation and error checking
- **Well-documented** - Clear output and instructions

If you encounter issues or need to update scripts:

1. Check script comments for implementation details
1. Review the generated SQL schema in `backend/supabase-schema.sql`
1. Manually verify in Supabase Dashboard if needed
1. Report issues with reproduction steps
