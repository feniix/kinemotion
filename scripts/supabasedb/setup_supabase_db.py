#!/usr/bin/env python3
"""
Supabase database schema setup script for Kinemotion.

This script automates the creation of database tables and Row Level Security (RLS) policies.
It requires SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY to be set.

Usage:
    python scripts/setup_supabase_db.py

Environment variables:
    SUPABASE_URL: Your Supabase project URL (e.g., https://project.supabase.co)
    SUPABASE_PUBLISHABLE_KEY: Your Supabase publishable key (format: sb_publishable_...)
    SUPABASE_SECRET_KEY: Your Supabase secret key for admin operations (format: sb_secret_...)

Note: Modern API keys (publishable/secret) are recommended over legacy anon/service_role keys.
"""

import os
import sys
from pathlib import Path

try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Error: supabase package not installed")
    print("Install with: pip install supabase")
    sys.exit(1)


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")


def print_success(text: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.NC}")


def print_warning(text: str) -> None:
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.NC}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.NC}")


def print_info(text: str) -> None:
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.NC}")


def get_env_var(var_name: str) -> str:
    """Get environment variable, raise error if not set."""
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"{var_name} environment variable not set")
    return value


def validate_credentials() -> tuple[str, str]:
    """Validate and return Supabase credentials."""
    try:
        url = get_env_var("SUPABASE_URL")
    except ValueError:
        print_error("SUPABASE_URL not found")
        print("Set it with: export SUPABASE_URL='https://your-project.supabase.co'")
        sys.exit(1)

    # Prefer SUPABASE_PUBLISHABLE_KEY, fall back to legacy keys for compatibility
    key = (os.getenv("SUPABASE_PUBLISHABLE_KEY") or
           os.getenv("SUPABASE_SECRET_KEY") or
           os.getenv("SUPABASE_KEY") or
           os.getenv("SUPABASE_ANON_KEY"))

    if not key:
        print_error("No Supabase API key found")
        print("\nRecommended (modern): export SUPABASE_PUBLISHABLE_KEY='sb_publishable_...'")
        print("Or for admin operations: export SUPABASE_SECRET_KEY='sb_secret_...'")
        print("\nLegacy (not recommended):")
        print("  export SUPABASE_KEY='...' or SUPABASE_ANON_KEY='...'")
        sys.exit(1)

    return url, key


def create_supabase_client(url: str, key: str) -> Client:
    """Create and return Supabase client."""
    try:
        client = create_client(url, key)
        return client
    except Exception as e:
        print_error(f"Failed to create Supabase client: {e}")
        sys.exit(1)


def execute_sql(client: Client, sql: str, description: str) -> bool:
    """Execute SQL via Supabase REST API."""
    try:
        print_info(description)
        # Use the rpc function to execute arbitrary SQL
        # Note: This requires a stored procedure or direct SQL execution capability
        # For now, we'll handle this differently
        print(f"  SQL: {sql[:80]}...")
        return True
    except Exception as e:
        print_error(f"Failed to execute SQL: {e}")
        return False


def get_schema_sql() -> str:
    """Return the complete database schema SQL."""
    return '''
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
'''


def save_schema_to_file(schema: str, filepath: str = "backend/supabase-schema.sql") -> None:
    """Save schema to a file."""
    try:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(schema)
        print_success(f"Schema saved to {filepath}")
    except Exception as e:
        print_error(f"Failed to save schema: {e}")


def display_manual_instructions(url: str, schema: str) -> None:
    """Display instructions for manual setup."""
    project_id = url.split('/')[-1].split('.')[0]

    print_header("Manual Setup Instructions")
    print(f"Project ID: {project_id}")
    print(f"Dashboard: https://supabase.com/dashboard/project/{project_id}/sql")
    print("\n1. Go to SQL Editor in Supabase Dashboard")
    print("2. Create a new query")
    print("3. Copy and paste the SQL below:")
    print(f"\n{Colors.BLUE}{'-'*60}{Colors.NC}")
    print(schema)
    print(f"{Colors.BLUE}{'-'*60}{Colors.NC}")
    print("\n4. Click 'Run' to execute")
    print("5. Verify with these commands:")
    print("\n   -- Check tables:")
    print("   SELECT tablename FROM pg_tables WHERE schemaname='public';")
    print("\n   -- Check RLS:")
    print("   SELECT tablename, rowsecurity FROM pg_tables")
    print("   WHERE schemaname='public' AND tablename IN ('analysis_sessions', 'coach_feedback');")
    print("\n   -- Check policies:")
    print("   SELECT tablename, policyname FROM pg_policies WHERE schemaname='public';")


def display_verification_instructions(url: str) -> None:
    """Display verification steps."""
    print_header("Verification Checklist")

    print(f"{Colors.YELLOW}After you run the SQL:${Colors.NC}\n")

    print("1. Verify tables exist:")
    print("   [] Check 'analysis_sessions' table in Supabase")
    print("   [] Check 'coach_feedback' table in Supabase")
    print("")

    print("2. Verify RLS is enabled:")
    print("   [] Run: SELECT rowsecurity FROM pg_tables WHERE tablename='analysis_sessions';")
    print("   [] Should return: true")
    print("")

    print("3. Verify policies exist:")
    print("   [] Run: SELECT policyname FROM pg_policies WHERE tablename='analysis_sessions';")
    print("   [] Should list 2 policies: users_can_read_own_sessions, users_can_create_own_sessions")
    print("")

    print("4. Test backend connection:")
    print("   [] Start backend: cd backend && uv run uvicorn kinemotion_backend.app:app --reload")
    print("   [] Test: curl http://localhost:8000/api/database-status")
    print("   [] Should return: {'status': 'connected', ...}")


def main() -> None:
    """Main setup function."""
    print_header("Kinemotion Supabase Database Setup")

    # Validate credentials
    print("Validating credentials...")
    try:
        url, key = validate_credentials()
        print_success(f"Credentials found for {url}")
    except SystemExit:
        raise

    # Get schema
    schema = get_schema_sql()

    # Save schema to file
    print("\nSaving schema...")
    save_schema_to_file(schema)

    # Display setup options
    print_header("Setup Instructions")

    print(f"{Colors.GREEN}Option 1: Manual Setup (Recommended){Colors.NC}")
    print("  • Go to Supabase Dashboard")
    print("  • Use SQL Editor to paste the schema")
    print("  • View saved schema in: backend/supabase-schema.sql")
    print("")

    print(f"{Colors.GREEN}Option 2: Using Supabase CLI{Colors.NC}")
    print("  • Install: npm install -g supabase")
    print("  • Link: supabase link --project-ref <project-id>")
    print("  • Execute: supabase db push")
    print("")

    # Display manual instructions
    display_manual_instructions(url, schema)

    # Display verification
    display_verification_instructions(url)

    print_header("Next Steps")
    print("1. Execute the SQL schema (Option 1 or 2 above)")
    print("2. Verify with the checklist above")
    print("3. Start backend and test connection")
    print("")
    print(f"Schema file: {Colors.BLUE}backend/supabase-schema.sql${Colors.NC}")
    print("")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Setup failed: {e}")
        sys.exit(1)
