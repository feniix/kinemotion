# E2E Tests

Playwright end-to-end tests for Kinemotion frontend.

## Authentication

Tests use **email/password authentication** - fully automated, no session files needed.

### Setting up GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

| Secret               | Value                   |
| -------------------- | ----------------------- |
| `TEST_USER_EMAIL`    | Test user email address |
| `TEST_USER_PASSWORD` | Test user password      |

**Recommended:** Create a dedicated test account (not your personal account).

### Local Development

Set environment variables before running tests locally:

```bash
# Option 1: Export in shell
export TEST_USER_EMAIL="test@example.com"
export TEST_USER_PASSWORD="yourpassword"
bun run test:e2e

# Option 2: Pass inline
TEST_USER_EMAIL="test@example.com" TEST_USER_PASSWORD="yourpassword" bun run test:e2e

# Option 3: Create .env.test.local (gitignored)
echo "TEST_USER_EMAIL=test@example.com" > .env.test.local
echo "TEST_USER_PASSWORD=yourpassword" >> .env.test.local
```

## Setup

### 1. Install Dependencies

```bash
cd frontend
bun install
```

### 2. Install Playwright Browsers

```bash
bunx playwright install --with-deps
```

## Running Tests

```bash
# Run all E2E tests (headless)
bun run test:e2e

# Run with UI mode (recommended for development)
bun run test:e2e:ui

# Run with visible browser (debugging)
bun run test:e2e:headed

# Debug mode with inspector
bun run test:e2e:debug

# Generate test code from browser interactions
bun run test:e2e:codegen
```

## Test Structure

```
e2e/
├── helpers/
│   └── auth.ts             # Auth helper (signIn, signOut, ensureSignedIn)
├── tests/
│   ├── auth.spec.ts        # Authentication flow tests
│   ├── upload.spec.ts      # Video upload flow tests
│   └── results.spec.ts     # Results display tests
└── fixtures/
    ├── cmj-45-IMG_6733.MOV     # CMJ test video (45° camera angle)
    └── dj-45-IMG_6739.MOV      # Drop Jump test video (45° camera angle)
```

## CI/CD

Tests run automatically on:

- Push to `main` branch
- Pull requests to `main`

The workflow (`.github/workflows/e2e.yml`) uses environment variables for credentials.

## Troubleshooting

**Tests fail with "Invalid login credentials"**

- Verify TEST_USER_EMAIL and TEST_USER_PASSWORD are correct
- Ensure the test user exists in Supabase

**Tests timeout**

- Network issues - check backend health
- Video processing slow - tests have 180s timeout for real video uploads

**Browser not installed**

- Run `bunx playwright install --with-deps`

**Tests work locally but fail in CI**

- Verify GitHub Secrets are set correctly
- Check that email auth is enabled in Supabase
