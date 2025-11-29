# Kinemotion Web UI

React frontend for Kinemotion video-based kinematic analysis.

## Features

- Video upload with drag-and-drop support
- Jump type selection (CMJ, Drop Jump)
- Real-time analysis progress
- Metrics display in clean table format
- Mobile responsive design
- Error handling with user-friendly messages
- TypeScript strict mode
- Production-ready build configuration

## Tech Stack

- React 18
- TypeScript 5
- Vite 5
- Yarn package manager

## Setup

### Prerequisites

- Node.js 18+ (LTS recommended)
- Yarn 1.22+

### Installation

```bash
# Install dependencies
yarn install

# Copy environment variables
cp .env.example .env.local

# Update .env.local with your backend URL
# Development: VITE_API_URL=http://localhost:8000
# Production: VITE_API_URL=https://kinemotion-api.fly.dev
```

## Development

```bash
# Start development server (http://localhost:5173)
yarn dev

# Type check
yarn type-check

# Build for production
yarn build

# Preview production build
yarn preview
```

## Environment Variables

Create a `.env.local` file with:

```bash
VITE_API_URL=http://localhost:8000  # Backend API URL
```

**Important:** Vite requires environment variables to be prefixed with `VITE_`. These are replaced at build time, not runtime.

## API Integration

The frontend communicates with the Kinemotion backend API:

**Endpoint:** `POST {VITE_API_URL}/api/analyze`

**Request:**

- Content-Type: multipart/form-data
- Fields:
  - `video`: Video file (max 500MB)
  - `jump_type`: "cmj" or "dropjump"

**Response:**

```json
{
  "metrics": {
    "jump_height": 45.2,
    "flight_time": 0.482,
    "ground_contact_time": 0.234,
    ...
  },
  "results_url": "https://...",  // Optional
  "analysis_time": 12.5  // Optional
}
```

**Error Response:**

```json
{
  "detail": "Error message"
}
```

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
yarn global add vercel

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

Or connect your GitHub repository to Vercel for automatic deployments.

**Environment Variables on Vercel:**

1. Go to Project Settings > Environment Variables
1. Add `VITE_API_URL` with your production backend URL
1. Redeploy

### Manual Build

```bash
# Build production bundle
yarn build

# Output directory: dist/
# Deploy the dist/ directory to any static hosting service
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── UploadForm.tsx   # File upload + jump type selector
│   │   ├── ResultsDisplay.tsx  # Metrics table display
│   │   ├── ErrorDisplay.tsx    # Error messages
│   │   └── LoadingSpinner.tsx  # Loading state
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # React entry point
│   └── index.css            # Global styles
├── index.html               # HTML entry point
├── vite.config.ts           # Vite configuration
├── tsconfig.json            # TypeScript configuration
├── vercel.json              # Vercel deployment config
└── package.json             # Dependencies
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari 14+, Chrome Android 90+)

## Performance

- Lazy loading for large videos
- Optimized bundle size with Vite
- Asset caching with service worker (future)
- Progressive Web App support (future)

## Troubleshooting

### File upload fails

- Check video file size (max 500MB)
- Verify video format (MP4, MOV, AVI)
- Ensure backend API is accessible

### CORS errors

- Backend must include frontend URL in CORS allowed origins
- Check `VITE_API_URL` in `.env.local`

### Build errors

- Clear node_modules: `rm -rf node_modules && yarn install`
- Clear Vite cache: `rm -rf node_modules/.vite`
- Update dependencies: `yarn upgrade`

## Contributing

See main repository [CLAUDE.md](../CLAUDE.md) for:

- Commit format (Conventional Commits)
- Code quality standards
- Testing requirements
- Type safety guidelines

## License

MIT License - See main repository for details
