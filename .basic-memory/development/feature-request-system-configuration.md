---
title: Feature Request System Configuration
type: note
permalink: development/feature-request-system-configuration
---

# Feature Request & Feedback System Configuration

## Frontend Configuration

### External Links Setup
Edit `frontend/src/config/links.ts`:

```typescript
export const EXTERNAL_LINKS = {
  // Replace with actual Google Forms URL
  FEATURE_REQUEST: 'https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform',
  GITHUB_ISSUES: 'https://github.com/feniix/kinemotion/issues',
  DOCUMENTATION: 'https://github.com/feniix/kinemotion#readme',
} as const

export const UI_CONFIG = {
  FEATURE_REQUEST: {
    enabled: true,
    buttonText: 'Request Feature',
    buttonIcon: '💡',
    tooltip: 'Share your ideas and suggestions for improving Kinemotion',
    openInNewTab: true,
  },
} as const
```

### Google Forms Setup

1. Create form at [Google Forms](https://forms.google.com)
2. Include fields:
   - Feature category (Analysis, UI, Performance, etc.)
   - Feature description
   - Use case/priority
   - Additional comments
3. Get form URL and update FEATURE_REQUEST constant

## Component Usage

### FeatureRequestButton Props
```typescript
<FeatureRequestButton
  variant="primary"     // or "secondary"
  size="medium"          // "small", "medium", "large"
  showIcon={true}
  className="custom-class"
/>
```

### Button Styles
- **Primary**: Blue background (`#6366f1`), white text
- **Secondary**: Light gray background (`#f3f4f6`), dark text
- **Sizes**: Small (0.75rem font), Medium (0.875rem), Large (1rem font)

## Database Detection

The frontend automatically detects backend database connectivity:

```typescript
const { status: dbStatus, loading: dbLoading } = useDatabaseStatus()

// Conditional UI rendering
{dbStatus?.database_connected && (
  <button>Add Coach Feedback</button>
)}

{!dbStatus?.database_connected && (
  <span>Database Offline - Feedback Unavailable</span>
)}
```

## Files Created
- `frontend/src/components/FeatureRequestButton.tsx`
- `frontend/src/components/FeedbackForm.tsx`
- `frontend/src/hooks/useDatabaseStatus.ts`
- `frontend/src/config/links.ts`

## Integration Points
- **ResultsDisplay**: Dedicated feedback section
- **Health Check**: Database status in `/health` endpoint
- **Analytics**: Google Analytics tracking included

## User Flow
1. Analysis completes → Results display
2. "Share Your Feedback" section appears
3. Options based on database status:
   - Database connected: Coach feedback + feature request + report issue
   - Database offline: Feature request + report issue + error message
4. Feature request opens Google Forms in new tab
5. Coach feedback saves to Supabase (if connected)

This system provides comprehensive user feedback collection while maintaining a seamless experience.
