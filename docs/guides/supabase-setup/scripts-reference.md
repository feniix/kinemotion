# Supabase Database Setup Scripts

Scripts for automating Supabase database schema creation and configuration.

## Quick Start

### 1. Set Environment Variables

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="sb_anon_your-key"
```

### 2. Run Setup Script

**Option A: Bash Script** (Recommended)

```bash
./setup-supabase-database.sh
```

**Option B: Python Script**

```bash
python setup_supabase_db.py
```

### 3. Execute SQL

Copy the displayed SQL schema into Supabase Dashboard → SQL Editor → Run

## Scripts

### `setup-supabase-database.sh`

Bash script that displays database schema and setup instructions.

```bash
./setup-supabase-database.sh
```

**Features:**

- ✅ Validates environment variables
- ✅ Displays complete SQL schema
- ✅ Shows 3 setup options (manual, CLI, automated)
- ✅ Provides verification checklist
- ✅ Includes next steps

**Requires:**

- `SUPABASE_URL` environment variable
- `SUPABASE_KEY` or `SUPABASE_ANON_KEY` environment variable

______________________________________________________________________

### `setup_supabase_db.py`

Python script for schema generation with validation and file output.

```bash
python setup_supabase_db.py
```

**Features:**

- ✅ Validates Supabase credentials
- ✅ Generates SQL schema
- ✅ Saves to `backend/supabase-schema.sql`
- ✅ Colored terminal output
- ✅ Detailed verification instructions
- ✅ Cross-platform compatible

**Requires:**

- Python 3.10+
- `SUPABASE_URL` environment variable
- `SUPABASE_KEY` or `SUPABASE_ANON_KEY` environment variable

______________________________________________________________________

## Setup Workflow

### Stage 1: Environment Configuration

```bash
cd ../..  # Go to project root
./scripts/setup-supabase-local.sh
# Creates: backend/.env, frontend/.env.local
```

### Stage 2: Database Schema

```bash
cd scripts/supabasedb
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="sb_anon_your-key"

# Option A: Bash
./setup-supabase-database.sh

# Option B: Python
python setup_supabase_db.py
```

### Stage 3: Execute SQL

1. Copy SQL from script output
1. Go to: https://supabase.com/dashboard/project/YOUR_PROJECT_ID/sql
1. Create new query and paste SQL
1. Click "Run"

### Stage 4: Verify

```bash
curl http://localhost:8000/api/database-status
```

______________________________________________________________________

## Database Schema

**Tables Created:**

- `analysis_sessions` - Video analysis results (JSONB storage)
- `coach_feedback` - Coach feedback on analyses

**Security:**

- Row Level Security (RLS) enabled
- 5 RLS policies for authorization
- Indexes for performance

**Full Details:**
See `SETUP_GUIDE.md` or `../../docs/development/supabase-database-setup.md`

______________________________________________________________________

## Environment Variables

### Required

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=sb_anon_your-key
```

### Alternative Names

```env
SUPABASE_ANON_KEY=sb_anon_your-key          # Works instead of SUPABASE_KEY
SUPABASE_SERVICE_ROLE_KEY=sb_service_role_...  # For admin operations
```

______________________________________________________________________

## Troubleshooting

### "SUPABASE_URL not set"

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="sb_anon_your-key"
```

### "Database connection failed"

Check:

1. Supabase project is running (check dashboard)
1. Credentials are correct
1. Network connectivity

### "RLS policy violation"

Usually means:

- User ID doesn't match the policy
- Policy conditions are incorrect
- Check `auth.uid()` matches authenticated user

______________________________________________________________________

## Files

```
scripts/supabasedb/
├── README.md                      # This file
├── SETUP_GUIDE.md                 # Comprehensive setup documentation
├── setup-supabase-database.sh     # Bash setup script
└── setup_supabase_db.py           # Python setup script
```

______________________________________________________________________

## Documentation

- **Quick Start**: `../../SUPABASE_QUICKSTART.md`
- **Setup Guide**: `./SETUP_GUIDE.md`
- **Technical Docs**: `../../docs/development/supabase-database-setup.md`
- **Backend Docs**: `../../backend/docs/setup.md`

______________________________________________________________________

## Support

- **Supabase Docs**: https://supabase.com/docs
- **Backend Code**: `backend/src/kinemotion_backend/database.py`
- **Issues**: GitHub Issues
- **Questions**: See main README

______________________________________________________________________

## Next Steps

1. Set environment variables
1. Run a setup script
1. Execute SQL in Supabase
1. Verify tables and RLS
1. Test backend connection
1. Start frontend for full integration

For detailed instructions: See `SETUP_GUIDE.md`
