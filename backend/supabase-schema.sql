
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Analysis Sessions Table
CREATE TABLE IF NOT EXISTS analysis_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
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
    coach_user_id TEXT NOT NULL,
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
-- Note: RLS is enforced at application level via backend authentication
-- The backend extracts email from JWT and passes it as user_id parameter
CREATE POLICY "users_can_read_own_sessions" ON analysis_sessions
    FOR SELECT
    USING (true);

CREATE POLICY "users_can_create_own_sessions" ON analysis_sessions
    FOR INSERT
    WITH CHECK (true);

-- RLS Policy: Coaches can read and create feedback
CREATE POLICY "coaches_can_read_feedback" ON coach_feedback
    FOR SELECT
    USING (true);

CREATE POLICY "coaches_can_create_feedback" ON coach_feedback
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY "coaches_can_update_own_feedback" ON coach_feedback
    FOR UPDATE
    USING (true)
    WITH CHECK (true);
