# Feature Request System Setup

This guide explains how to configure the feature request and feedback system in the Kinemotion frontend.

## Overview

The frontend includes a comprehensive feedback system that allows users to:

- Submit coach feedback (when database is connected)
- Request new features via Google Forms
- Report issues on GitHub
- Share general feedback

## Configuration

### 1. Update Google Forms URL

Edit `frontend/src/config/links.ts` and update the `FEATURE_REQUEST` URL:

```typescript
export const EXTERNAL_LINKS = {
  // Replace with your actual Google Forms URL
  FEATURE_REQUEST: 'https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform',

  // Other links...
  GITHUB_ISSUES: 'https://github.com/feniix/kinemotion/issues',
  // ...
}
```

### 2. Create Your Google Form

1. Go to [Google Forms](https://forms.google.com)

1. Create a new form for feature requests

1. Include fields like:

   - Name/Email (optional)
   - Feature category (Analysis, UI, Performance, etc.)
   - Feature description
   - Use case/priority
   - Additional comments

1. Get the form URL:

   - Click "Send" (top right)
   - Click the link icon (🔗)
   - Copy the URL
   - Update the `FEATURE_REQUEST` constant in `links.ts`

### 3. Customize Button Appearance

Edit `frontend/src/config/links.ts` to customize the feature request button:

```typescript
export const UI_CONFIG = {
  FEATURE_REQUEST: {
    enabled: true,                    // Show/hide the button
    buttonText: 'Request Feature',    // Button text
    buttonIcon: '💡',                // Emoji or icon
    tooltip: 'Share your ideas...',  // Hover tooltip
    openInNewTab: true,              // Open in new tab
  },
  // ...
}
```

## Component Usage

### FeatureRequestButton Component

```typescript
import FeatureRequestButton from '../components/FeatureRequestButton'

// Basic usage
<FeatureRequestButton />

// With options
<FeatureRequestButton
  variant="primary"     // or "secondary"
  size="medium"          // "small", "medium", "large"
  showIcon={true}
  className="my-custom-class"
/>
```

### Integration in ResultsDisplay

The feature request system is integrated into the `ResultsDisplay` component in a dedicated feedback section:

1. **Coach Feedback Button**: Only shows when database is connected
1. **Feature Request Button**: Always available, opens Google Forms
1. **Report Issue Button**: Links to GitHub Issues

## Analytics Tracking

The feature request button includes Google Analytics event tracking by default:

```javascript
// Tracks when users click the feature request button
window.gtag('event', 'feature_request_click', {
  event_category: 'engagement',
  event_label: 'feature_request_button',
})
```

To disable this, remove the analytics tracking from `FeatureRequestButton.tsx`.

## Styling

The buttons use inline styles for easy customization. You can modify the styles by:

1. **Editing Component Styles**: Update `FeatureRequestButton.tsx`
1. **Using CSS Classes**: Add custom CSS classes via the `className` prop
1. **Theme Customization**: Modify colors in the component variants

## Button Variants

### Primary Variant

- Blue background (`#6366f1`)
- White text
- For main calls-to-action

### Secondary Variant

- Light gray background (`#f3f4f6`)
- Dark text
- For secondary actions

## Sizes

- **Small**: `0.5rem 1rem` padding, `0.75rem` font
- **Medium**: `0.75rem 1.5rem` padding, `0.875rem` font (default)
- **Large**: `1rem 2rem` padding, `1rem` font

## Testing the Integration

1. **Backend Running**: Ensure the backend is running
1. **Database Status**: Test with database connected/disconnected
1. **Button Functionality**: Verify buttons open correct URLs
1. **Responsive Design**: Test on different screen sizes

## Example User Flow

1. User completes video analysis
1. Results display with metrics
1. User sees "Share Your Feedback" section
1. Options based on database status:
   - **Database Connected**: Coach feedback + feature request + report issue
   - **Database Offline**: Feature request + report issue + status message
1. Clicking feature request opens Google Forms in new tab
1. User can submit feedback without interrupting their workflow

## Files Structure

```
frontend/src/
├── components/
│   ├── FeatureRequestButton.tsx    # Reusable feature request button
│   └── ResultsDisplay.tsx          # Updated with feedback section
├── hooks/
│   └── useDatabaseStatus.ts        # Database connection detection
├── config/
│   └── links.ts                    # External links and UI configuration
└── types/
    └── api.ts                      # Type definitions
```

## Troubleshooting

### Button Not Showing

- Check `FEATURE_REQUEST.enabled` is `true` in `links.ts`
- Verify the Google Forms URL is set correctly
- Check browser console for JavaScript errors

### Link Not Working

- Verify the Google Forms URL is accessible
- Check for pop-up blockers if new tab isn't opening
- Test the URL directly in browser

### Styling Issues

- Check for CSS conflicts
- Verify styles are not being overridden
- Test with different browsers

This system provides a seamless way for users to provide feedback and request features while maintaining a clean user experience.
