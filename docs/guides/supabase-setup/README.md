# Supabase Setup Guide

Complete guide for setting up the Supabase database and configuring the Kinemotion backend for data persistence.

## Quick Navigation

- **[quickstart.md](quickstart.md)** - 5-minute setup guide (start here!)
- **[setup-guide.md](setup-guide.md)** - Comprehensive setup instructions
- **[scripts-reference.md](scripts-reference.md)** - Setup scripts documentation
- **[../development/supabase-database-setup.md](../development/supabase-database-setup.md)** - Technical deep-dive

## For Impatient Developers

Read [quickstart.md](quickstart.md) and run:

```bash
./scripts/setup-supabase-local.sh
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="sb_anon_your-key"
./scripts/supabasedb/setup-supabase-database.sh
```

Copy SQL into Supabase Dashboard and test!

## For Complete Understanding

1. Read [setup-guide.md](setup-guide.md) for step-by-step instructions
1. See [scripts-reference.md](scripts-reference.md) for script options
1. Check [../development/supabase-database-setup.md](../development/supabase-database-setup.md) for technical details

## What Gets Set Up

- **Tables**: `analysis_sessions`, `coach_feedback`
- **Security**: Row Level Security (RLS) with 5 policies
- **Performance**: 4 indexes for query optimization
- **Backend Connection**: FastAPI integration with Supabase

## Setup Scripts Location

Scripts are in `scripts/supabasedb/`:

- `setup-supabase-database.sh` - Bash setup script
- `setup_supabase_db.py` - Python setup script

## Environment Variables

After setup, you'll have:

- `backend/.env` - Backend Supabase configuration
- `frontend/.env.local` - Frontend Supabase configuration

## Support

- **Issues**: GitHub Issues
- **Questions**: See backend/docs/setup.md
- **Technical**: See docs/development/supabase-database-setup.md
