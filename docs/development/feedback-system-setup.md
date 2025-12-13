# Coach Feedback System Setup

This guide covers setting up the Supabase database integration for storing analysis sessions and coach feedback.

## Overview

The feedback system allows coaches to:

- Store analysis sessions with video references and JSON results
- Add ratings, notes, and tags to analyses
- Track athlete progress over time
- Query stored data for insights

## Prerequisites

- A Supabase project (already configured for kinemotion)
- Supabase project URL and anon key configured in environment variables

## Database Setup

### 1. Create Tables

Run the SQL from `backend/supabase-schema.sql` in your Supabase SQL Editor:

1. Go to your Supabase project dashboard
1. Click on "SQL Editor" in the left sidebar
1. Click "New query"
1. Copy and paste the contents of `backend/supabase-schema.sql`
1. Click "Run"

This will create:

- `analysis_sessions` table for storing analysis metadata
- `coach_feedback` table for storing coach notes and ratings
- Proper indexes and Row Level Security (RLS) policies
- A view for combined analysis sessions with feedback

### 2. Verify Environment Variables

Ensure your backend has these environment variables set:

```bash
SUPABASE_URL=your-supabase-project-url
SUPABASE_ANON_KEY=your-supabase-anon-key
```

These should already be configured in your Google Cloud Run deployment.

## Backend Integration

### Database Client (`backend/src/kinemotion_backend/database.py`)

- Async Supabase client integration
- CRUD operations for sessions and feedback
- Error handling and logging

### API Endpoints (`backend/src/kinemotion_backend/analysis_api.py`)

- `POST /api/analysis/sessions` - Create analysis sessions
- `GET /api/analysis/sessions` - List user's sessions
- `GET /api/analysis/sessions/{id}` - Get specific session
- `POST /api/analysis/sessions/{id}/feedback` - Add coach feedback
- `GET /api/analysis/database-status` - Check database connection

### Main App Integration

- Modified `/api/analyze` endpoint to optionally save sessions
- Graceful fallback if user not authenticated
- Non-blocking database operations

## Frontend Integration

### Feedback Form (`frontend/src/components/FeedbackForm.tsx`)

- Star rating system (1-5)
- Pre-defined and custom tags
- Rich text notes field
- Modal interface

### Results Display Integration

- "Add Coach Feedback" button appears with analysis results
- Modal form for feedback submission
- Integrates with Supabase authentication

### Database Connection Detection

- `useDatabaseStatus` hook checks backend database status
- Conditional display of feedback features
- User-friendly status indicators

## How It Works

### Analysis Flow

1. **User Uploads Video**: Existing flow unchanged
1. **Video Analysis**: Backend processes video with kinemotion CLI
1. **Optional Storage**: If user is authenticated, analysis session is saved to Supabase
1. **Display Results**: Frontend shows metrics as before
1. **Coach Feedback**: Coaches can add feedback via the new form

### Data Storage

- **Analysis Sessions**: Store metadata, R2 URLs, and full JSON results
- **Coach Feedback**: Store ratings, notes, and tags linked to sessions
- **JSONB Storage**: Analysis results stored as JSONB for flexible querying
- **Security**: RLS ensures users can only access their own data

## Example Queries

```sql
-- Get average jump height by user
SELECT
  user_id,
  AVG((analysis_data->'data'->>'jump_height')::float) as avg_jump_height
FROM analysis_sessions
WHERE jump_type = 'cmj'
GROUP BY user_id;

-- Find sessions with coach feedback
SELECT
  s.id,
  s.jump_type,
  s.created_at,
  f.rating,
  f.notes
FROM analysis_sessions s
LEFT JOIN coach_feedback f ON s.id = f.analysis_session_id
WHERE f.id IS NOT NULL;

-- Get sessions with high RSI scores
SELECT *
FROM analysis_sessions
WHERE jump_type = 'drop_jump'
  AND (analysis_data->'data'->>'reactive_strength_index')::float > 2.0;
```

## Testing the Integration

1. **Backend Testing**:

   ```bash
   cd backend
   uv run pytest  # Tests should pass
   ```

1. **Frontend Testing**:

   - Upload a video while logged in
   - After analysis completes, click "Add Coach Feedback"
   - Fill out the feedback form and submit
   - Check that data appears in Supabase dashboard

1. **Database Verification**:

   - Check Supabase dashboard > Table Editor
   - Verify data appears in `analysis_sessions` and `coach_feedback` tables

## Troubleshooting

### Common Issues

1. **Database Connection Failed**:

   - Verify SUPABASE_URL and SUPABASE_ANON_KEY are set
   - Check Supabase project is active

1. **Permission Denied**:

   - Ensure RLS policies are correctly applied
   - Check user authentication is working

1. **Feedback Not Saving**:

   - Ensure user is logged in (Supabase auth)
   - Check browser console for error messages
   - Verify API endpoints are accessible

### Debug Logging

The system logs detailed information:

- Check backend logs for database operations
- Frontend console shows API call details
- Supabase dashboard shows query logs

## Security Notes

- RLS policies ensure data privacy
- JWT tokens are validated for all API calls
- Users can only access their own analysis sessions
- Feedback is visible to all authenticated users (for collaboration)
