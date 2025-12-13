-- Supabase Database Schema for Kinemotion Analysis Sessions
--
-- Run this SQL in your Supabase SQL Editor to create the required tables

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Analysis Sessions Table
CREATE TABLE IF NOT EXISTS analysis_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    jump_type VARCHAR(50) NOT NULL CHECK (jump_type IN ('cmj', 'drop_jump')),
    quality_preset VARCHAR(20) NOT NULL CHECK (quality_preset IN ('fast', 'balanced', 'accurate')),

    -- R2 Storage references
    original_video_url TEXT,
    debug_video_url TEXT,
    results_json_url TEXT,

    -- Analysis results stored as JSONB for flexible querying
    analysis_data JSONB NOT NULL,

    -- Processing metadata
    processing_time_s FLOAT,
    upload_id VARCHAR(50),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Coach Feedback Table
CREATE TABLE IF NOT EXISTS coach_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_session_id UUID NOT NULL REFERENCES analysis_sessions(id) ON DELETE CASCADE,
    coach_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Feedback content
    notes TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    tags TEXT[] DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_analysis_sessions_updated_at
    BEFORE UPDATE ON analysis_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_coach_feedback_updated_at
    BEFORE UPDATE ON coach_feedback
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_analysis_sessions_user_id ON analysis_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_sessions_jump_type ON analysis_sessions(jump_type);
CREATE INDEX IF NOT EXISTS idx_analysis_sessions_created_at ON analysis_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_sessions_upload_id ON analysis_sessions(upload_id);

-- JSONB GIN index for flexible querying of analysis data
CREATE INDEX IF NOT EXISTS idx_analysis_sessions_analysis_data ON analysis_sessions USING GIN(analysis_data);

-- Indexes for coach feedback
CREATE INDEX IF NOT EXISTS idx_coach_feedback_session_id ON coach_feedback(analysis_session_id);
CREATE INDEX IF NOT EXISTS idx_coach_feedback_coach_id ON coach_feedback(coach_user_id);
CREATE INDEX IF NOT EXISTS idx_coach_feedback_created_at ON coach_feedback(created_at DESC);

-- Row Level Security (RLS)

-- Enable RLS on both tables
ALTER TABLE analysis_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE coach_feedback ENABLE ROW LEVEL SECURITY;

-- RLS Policies for analysis_sessions
-- Users can read their own analysis sessions
CREATE POLICY "Users can view own analysis sessions" ON analysis_sessions
    FOR SELECT USING (auth.uid() = user_id);

-- Users can insert their own analysis sessions
CREATE POLICY "Users can insert own analysis sessions" ON analysis_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own analysis sessions
CREATE POLICY "Users can update own analysis sessions" ON analysis_sessions
    FOR UPDATE USING (auth.uid() = user_id);

-- Users can delete their own analysis sessions
CREATE POLICY "Users can delete own analysis sessions" ON analysis_sessions
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for coach_feedback
-- All authenticated users can view feedback (for collaboration)
CREATE POLICY "Authenticated users can view feedback" ON coach_feedback
    FOR SELECT USING (auth.role() = 'authenticated');

-- All authenticated users can insert feedback
CREATE POLICY "Authenticated users can create feedback" ON coach_feedback
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Users can update their own feedback
CREATE POLICY "Users can update own feedback" ON coach_feedback
    FOR UPDATE USING (auth.uid() = coach_user_id);

-- Users can delete their own feedback
CREATE POLICY "Users can delete own feedback" ON coach_feedback
    FOR DELETE USING (auth.uid() = coach_user_id);

-- Grant permissions
GRANT ALL ON analysis_sessions TO authenticated;
GRANT ALL ON coach_feedback TO authenticated;
GRANT ALL ON analysis_sessions TO service_role;
GRANT ALL ON coach_feedback TO service_role;

-- Optional: Create a view for common queries
CREATE OR REPLACE VIEW analysis_sessions_with_feedback AS
SELECT
    a.*,
    COALESCE(
        json_agg(
            json_build_object(
                'id', f.id,
                'coach_user_id', f.coach_user_id,
                'notes', f.notes,
                'rating', f.rating,
                'tags', f.tags,
                'created_at', f.created_at
            ) ORDER BY f.created_at DESC
        ) FILTER (WHERE f.id IS NOT NULL),
        '[]'::json
    ) as feedback
FROM analysis_sessions a
LEFT JOIN coach_feedback f ON a.id = f.analysis_session_id
GROUP BY a.id, a.user_id, a.jump_type, a.quality_preset,
         a.original_video_url, a.debug_video_url, a.results_json_url,
         a.analysis_data, a.processing_time_s, a.upload_id,
         a.created_at, a.updated_at;
