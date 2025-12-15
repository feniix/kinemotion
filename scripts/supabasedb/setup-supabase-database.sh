#!/bin/bash
# Setup Supabase database schema for Kinemotion
# This script creates tables and Row Level Security (RLS) policies
# Run this AFTER setting up environment variables with setup-supabase-local.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🗄️  Setting up Supabase database schema...${NC}"
echo ""

# Check if SUPABASE_URL is set
if [ -z "$SUPABASE_URL" ]; then
    echo -e "${RED}❌ Error: SUPABASE_URL is not set${NC}"
    echo "Please run setup-supabase-local.sh first or set environment variables:"
    echo "  export SUPABASE_URL='https://your-project.supabase.co'"
    echo "  export SUPABASE_PUBLISHABLE_KEY='sb_publishable_...'"
    exit 1
fi

# Prefer modern keys, fall back to legacy for compatibility
if [ -z "$SUPABASE_PUBLISHABLE_KEY" ] && [ -z "$SUPABASE_SECRET_KEY" ] && \
   [ -z "$SUPABASE_KEY" ] && [ -z "$SUPABASE_ANON_KEY" ]; then
    echo -e "${RED}❌ Error: No Supabase API key found${NC}"
    echo ""
    echo "Recommended (modern): export SUPABASE_PUBLISHABLE_KEY='sb_publishable_...'"
    echo "Or for admin operations: export SUPABASE_SECRET_KEY='sb_secret_...'"
    echo ""
    echo "Legacy (not recommended):"
    echo "  export SUPABASE_KEY='...' or SUPABASE_ANON_KEY='...'"
    exit 1
fi

# Use SUPABASE_PUBLISHABLE_KEY if set, otherwise fall back to legacy keys
API_KEY="${SUPABASE_PUBLISHABLE_KEY:-${SUPABASE_SECRET_KEY:-${SUPABASE_KEY:-$SUPABASE_ANON_KEY}}}"

echo -e "${BLUE}Project URL:${NC} $SUPABASE_URL"
echo ""

# Extract project ID from URL
PROJECT_ID=$(echo $SUPABASE_URL | sed 's/.*\/\///;s/\.supabase\.co.*//')

# Function to execute SQL via Supabase REST API
execute_sql() {
    local sql="$1"
    local description="$2"

    echo -ne "${YELLOW}⏳ ${description}...${NC}"

    # Use the REST API to execute SQL
    # Note: SQL execution via REST API requires proper setup
    # For now, we'll provide the SQL and instructions
    echo ""
    echo -e "${BLUE}SQL:${NC}"
    echo "$sql"
    echo ""
}

# SQL Schema Definition
SQL_SCHEMA='
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Analysis Sessions Table
CREATE TABLE IF NOT EXISTS analysis_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    jump_type VARCHAR(50) NOT NULL CHECK (jump_type IN ('"'"'cmj'"'"', '"'"'drop_jump'"'"')),
    quality_preset VARCHAR(20) NOT NULL CHECK (quality_preset IN ('"'"'fast'"'"', '"'"'balanced'"'"', '"'"'accurate'"'"')),
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
    tags TEXT[] DEFAULT '"'"'{}'"'"',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_analysis_sessions_user_id ON analysis_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_sessions_created_at ON analysis_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_coach_feedback_analysis_session_id ON coach_feedback(analysis_session_id);
CREATE INDEX IF NOT EXISTS idx_coach_feedback_coach_user_id ON coach_feedback(coach_user_id);

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

-- RLS Policy: Coaches can read feedback for their own analyses or sessions they'"'"'re coaching
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
'

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Database Setup Instructions${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${GREEN}✅ Option 1: Manual Setup (Recommended for first-time setup)${NC}"
echo ""
echo "1. Go to Supabase Dashboard: https://supabase.com/dashboard"
echo "2. Select your project: $PROJECT_ID"
echo "3. Go to SQL Editor → New Query"
echo "4. Copy and paste the SQL below:"
echo ""
echo -e "${BLUE}────────────────────────────────────────────────────────${NC}"
echo "$SQL_SCHEMA"
echo -e "${BLUE}────────────────────────────────────────────────────────${NC}"
echo ""
echo "5. Click 'Run' to execute the schema"
echo "6. Verify tables were created: SQL Editor → Show all tables"
echo ""

echo -e "${GREEN}✅ Option 2: Automated Setup (Using Supabase CLI)${NC}"
echo ""
echo "If you have Supabase CLI installed:"
echo ""
echo "  # Save SQL to file"
echo "  cat > /tmp/kinemotion-schema.sql << 'SCHEMA_EOF'"
echo "$SQL_SCHEMA"
echo "SCHEMA_EOF"
echo ""
echo "  # Link to your project"
echo "  supabase link --project-ref $PROJECT_ID"
echo ""
echo "  # Execute schema"
echo "  supabase db push"
echo ""

echo -e "${GREEN}✅ Option 3: Verify Setup${NC}"
echo ""
echo "After setup, verify with these queries in SQL Editor:"
echo ""
echo "  -- Check tables exist"
echo "  SELECT tablename FROM pg_tables WHERE schemaname='public';"
echo ""
echo "  -- Check RLS is enabled"
echo "  SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname='public' AND tablename IN ('analysis_sessions', 'coach_feedback');"
echo ""
echo "  -- Check policies exist"
echo "  SELECT tablename, policyname FROM pg_policies WHERE schemaname='public';"
echo ""

echo -e "${YELLOW}⚠️  Environment Variables${NC}"
echo ""
echo "Your current setup:"
echo "  SUPABASE_URL: $SUPABASE_URL"
echo "  API_KEY: ${API_KEY:0:20}... (hidden)"
echo ""

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# Check if backend/.env exists
if [ -f "backend/.env" ]; then
    echo -e "${GREEN}✅ backend/.env exists${NC}"
    echo ""

    # Check if SUPABASE_URL is in backend/.env
    if grep -q "SUPABASE_URL=" backend/.env; then
        echo "✅ SUPABASE_URL configured in backend/.env"
    else
        echo -e "${YELLOW}⚠️  SUPABASE_URL not found in backend/.env${NC}"
        echo "Please add it manually or run setup-supabase-local.sh"
    fi

    if grep -q "SUPABASE_PUBLISHABLE_KEY=" backend/.env || grep -q "SUPABASE_SECRET_KEY=" backend/.env || grep -q "SUPABASE_KEY=" backend/.env || grep -q "SUPABASE_ANON_KEY=" backend/.env; then
        echo "✅ Supabase API key configured in backend/.env"
    else
        echo -e "${YELLOW}⚠️  No Supabase API key found in backend/.env${NC}"
        echo "Please add SUPABASE_PUBLISHABLE_KEY or SUPABASE_SECRET_KEY manually or run setup-supabase-local.sh"
    fi
else
    echo -e "${YELLOW}⚠️  backend/.env not found${NC}"
    echo "Run setup-supabase-local.sh first to create environment files"
fi

echo ""

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Setup instructions complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

echo "Next steps:"
echo "1. Execute the SQL schema in Supabase (Option 1 above)"
echo "2. Verify tables and RLS are set up (Option 3 above)"
echo "3. Start the backend: cd backend && uv run uvicorn kinemotion_backend.app:app --reload"
echo "4. Test connection: curl http://localhost:8000/api/database-status"
echo ""
echo "📚 Documentation:"
echo "  • Quick start: docs/guides/supabase-setup/quickstart.md"
echo "  • Full guide: docs/guides/supabase-setup/setup-guide.md"
echo "  • Technical: docs/development/supabase-database-setup.md"
echo ""
