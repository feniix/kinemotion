---
title: Supabase Database Integration Setup
type: note
permalink: development/supabase-database-integration-setup
---

# Supabase Database Integration for Coach Feedback

## Database Schema

Run this SQL in Supabase SQL Editor to create the required tables:

```sql
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

-- Indexes and RLS policies included in full schema
```

## Backend Integration

### New Files Created:
- `backend/src/kinemotion_backend/database.py` - Async Supabase client
- `backend/src/kinemotion_backend/analysis_api.py` - Feedback API endpoints
- `backend/src/kinemotion_backend/models.py` - Pydantic models
- `backend/supabase-schema.sql` - Complete database schema

### API Endpoints:
- `POST /api/analysis/sessions` - Create analysis sessions
- `GET /api/analysis/sessions` - List user sessions
- `GET /api/analysis/sessions/{id}` - Get session with feedback
- `POST /api/analysis/sessions/{id}/feedback` - Add coach feedback
- `GET /api/analysis/database-status` - Check database connection

### Key Features:
- Optional authentication (works with/without user login)
- JSONB storage for flexible analysis data querying
- Row Level Security for data privacy
- Async database operations
- Graceful error handling

## Frontend Integration

### Components Added:
- `FeedbackForm.tsx` - Modal feedback form with rating, tags, notes
- `FeatureRequestButton.tsx` - Reusable feature request button
- `useDatabaseStatus.ts` - Hook for checking database connectivity

### Configuration:
- `config/links.ts` - External links and UI settings
- Google Forms integration for feature requests
- Conditional UI based on database status

### User Experience:
- Smart feedback section with multiple options
- Database connection detection
- Responsive design
- Analytics tracking ready

## Setup Requirements:
1. Run database schema in Supabase
2. Configure SUPABASE_URL and SUPABASE_ANON_KEY
3. Update Google Forms URL in frontend config
4. Test integration with authenticated/unauthenticated users

## Example Queries:
```sql
-- Average jump height by user
SELECT user_id, AVG((analysis_data->'data'->>'jump_height')::float) as avg_jump_height
FROM analysis_sessions WHERE jump_type = 'cmj' GROUP BY user_id;

-- Sessions with feedback
SELECT s.*, f.rating, f.notes
FROM analysis_sessions s
LEFT JOIN coach_feedback f ON s.id = f.analysis_session_id
WHERE f.id IS NOT NULL;
```

This system enables comprehensive coach feedback collection and athlete performance tracking.
