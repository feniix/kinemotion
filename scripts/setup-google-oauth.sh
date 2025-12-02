#!/bin/bash
# Setup Google OAuth for Supabase authentication
# This script automates Google Cloud Console configuration for OAuth
# Run this script to configure Google OAuth credentials for Supabase
# This script is idempotent - safe to run multiple times

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration (can be overridden via environment variables)
PROJECT_ID="${GCP_PROJECT_ID:-kinemotion-backend}"
APP_NAME="${APP_NAME:-Kinemotion}"
SUPABASE_PROJECT_ID="${SUPABASE_PROJECT_ID:-}"
FRONTEND_URL="${FRONTEND_URL:-https://kinemotion.vercel.app}"
LOCAL_PORT="${LOCAL_PORT:-5173}"

echo -e "${BLUE}🔐 Google OAuth Setup for Supabase${NC}"
echo ""
echo "This script will:"
echo "  1. Check/install gcloud CLI"
echo "  2. Authenticate with Google Cloud"
echo "  3. Enable required APIs"
echo "  4. Guide you through OAuth consent screen setup"
echo "  5. Create OAuth client credentials"
echo "  6. Output credentials for Supabase configuration"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed${NC}"
    echo ""
    echo "Please install gcloud CLI:"
    echo "  macOS: brew install google-cloud-sdk"
    echo "  Linux: https://cloud.google.com/sdk/docs/install"
    echo "  Or visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo -e "${GREEN}✓ gcloud CLI found${NC}"

# Check if authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo ""
    echo -e "${YELLOW}⚠️  Not authenticated with Google Cloud${NC}"
    echo "Please authenticate:"
    gcloud auth login
else
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1)
    echo -e "${GREEN}✓ Authenticated as: $ACTIVE_ACCOUNT${NC}"
fi

# Set project
echo ""
echo "Setting project to: $PROJECT_ID"
if ! gcloud projects describe "$PROJECT_ID" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Project '$PROJECT_ID' not found${NC}"
    read -p "Create new project '$PROJECT_ID'? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gcloud projects create "$PROJECT_ID" --name="$APP_NAME"
        echo -e "${GREEN}✓ Created project '$PROJECT_ID'${NC}"
    else
        read -p "Enter existing project ID: " PROJECT_ID
        gcloud config set project "$PROJECT_ID"
    fi
else
    gcloud config set project "$PROJECT_ID"
    echo -e "${GREEN}✓ Project set to '$PROJECT_ID'${NC}"
fi

# Get Supabase project ID if not provided
if [ -z "$SUPABASE_PROJECT_ID" ]; then
    echo ""
    echo -e "${YELLOW}Enter your Supabase project ID${NC}"
    echo "You can find this in Supabase Dashboard → Settings → API"
    echo "Format: https://<project-id>.supabase.co"
    read -p "Supabase project ID (e.g., 'smutfsalcbnfveqijttb'): " SUPABASE_PROJECT_ID
fi

# Validate Supabase project ID format (basic check)
if [[ ! "$SUPABASE_PROJECT_ID" =~ ^[a-z0-9]{20,}$ ]]; then
    echo -e "${YELLOW}⚠️  Warning: Supabase project ID format looks unusual${NC}"
    echo "  Expected: 20+ lowercase alphanumeric characters"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

SUPABASE_CALLBACK_URL="https://${SUPABASE_PROJECT_ID}.supabase.co/auth/v1/callback"
LOCAL_CALLBACK_URL="http://localhost:3000/auth/v1/callback"

echo ""
echo -e "${BLUE}📦 Enabling required APIs...${NC}"
if ! gcloud services enable \
    cloudresourcemanager.googleapis.com \
    --project="$PROJECT_ID" 2>&1; then
    echo "  APIs already enabled or error occurred"
fi
echo -e "${GREEN}✓ APIs enabled${NC}"

# Check OAuth consent screen (idempotent check)
echo ""
echo -e "${BLUE}🔍 Checking OAuth consent screen configuration...${NC}"
echo ""
read -p "Is OAuth consent screen already configured? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    CONSENT_CONFIGURED=true
else
    CONSENT_CONFIGURED=false
fi

if [ "$CONSENT_CONFIGURED" = false ]; then
    echo ""
    echo "You need to configure the OAuth consent screen (one-time setup):"
    echo ""
    CONSENT_URL="https://console.cloud.google.com/apis/credentials/consent?project=$PROJECT_ID"
    echo -e "${YELLOW}Step 1: Configure OAuth Consent Screen${NC}"
    echo "  Visit: ${BLUE}$CONSENT_URL${NC}"

    # Try to open browser (macOS/Linux)
    if command -v open &> /dev/null; then
        read -p "Open browser to OAuth consent screen? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open "$CONSENT_URL"
        fi
    elif command -v xdg-open &> /dev/null; then
        read -p "Open browser to OAuth consent screen? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            xdg-open "$CONSENT_URL"
        fi
    fi
    echo ""
    echo "  Instructions:"
    echo "    1. Choose 'External' (unless you have Google Workspace)"
    echo "    2. Fill in:"
    echo "       - App name: $APP_NAME"
    echo "       - User support email: (your email)"
    echo "       - Developer contact: (your email)"
    echo "    3. Click 'Save and Continue'"
    echo "    4. Add scopes: email, profile, openid"
    echo "    5. Click 'Save and Continue'"
    echo "    6. Add test users if needed (for testing before verification)"
    echo "    7. Click 'Save and Continue' → 'Back to Dashboard'"
    echo ""
    read -p "Press Enter when OAuth consent screen is configured..."
fi

# Check for existing OAuth clients (idempotent check)
echo ""
echo -e "${BLUE}🔑 Checking for existing OAuth Clients${NC}"
echo ""

CREDENTIALS_URL="https://console.cloud.google.com/apis/credentials?project=$PROJECT_ID"
USE_EXISTING=false

# Note: gcloud doesn't have a direct command to list OAuth clients
# We'll guide the user to check manually
echo "To check for existing OAuth clients, visit:"
echo "  ${BLUE}$CREDENTIALS_URL${NC}"
echo ""
read -p "Do you already have an OAuth client configured? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    USE_EXISTING=true
fi

if [ "$USE_EXISTING" = true ]; then
    echo ""
    echo -e "${BLUE}📋 Enter Existing OAuth Client Credentials${NC}"
    echo ""
    read -p "Client ID: " CLIENT_ID

    # Validate Client ID format
    if [[ -n "$CLIENT_ID" && ! "$CLIENT_ID" =~ \.googleusercontent\.com$ ]]; then
        echo -e "${YELLOW}⚠️  Warning: CLIENT_ID format looks incorrect${NC}"
        echo "  Expected format: *.googleusercontent.com"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    read -p "Client Secret (leave empty if you don't have it): " CLIENT_SECRET

    if [ -z "$CLIENT_SECRET" ]; then
        echo ""
        echo -e "${YELLOW}⚠️  Client Secret not provided${NC}"
        echo "CLIENT_SECRET is required for Supabase configuration."
        echo "If you need to retrieve it:"
        echo "  1. Visit: $CREDENTIALS_URL"
        echo "  2. Click on your OAuth client"
        echo "  3. If secret is not visible, you may need to create a new client"
        echo ""
        read -p "Create a new OAuth client instead? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            USE_EXISTING=false
            CLIENT_ID=""
            CLIENT_SECRET=""
        else
            echo -e "${RED}❌ Cannot proceed without CLIENT_SECRET${NC}"
            exit 1
        fi
    fi
fi

if [ "$USE_EXISTING" = false ]; then
    echo ""
    echo -e "${YELLOW}Step 2: Create OAuth Client ID${NC}"
    echo "  Visit: ${BLUE}$CREDENTIALS_URL${NC}"

    # Try to open browser
    if command -v open &> /dev/null; then
        read -p "Open browser to create OAuth client? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open "$CREDENTIALS_URL"
        fi
    elif command -v xdg-open &> /dev/null; then
        read -p "Open browser to create OAuth client? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            xdg-open "$CREDENTIALS_URL"
        fi
    fi
    echo ""
    echo "  Instructions:"
    echo "    1. Click 'Create Credentials' → 'OAuth client ID'"
    echo "    2. Application type: ${GREEN}Web application${NC}"
    echo "    3. Name: ${GREEN}$APP_NAME OAuth Client${NC}"
    echo "    4. Authorized JavaScript origins (click 'Add URI' for each):"
    echo "       ${GREEN}$FRONTEND_URL${NC}"
    echo "       ${GREEN}http://localhost:$LOCAL_PORT${NC}"
    echo "    5. Authorized redirect URIs (click 'Add URI' for each):"
    echo "       ${GREEN}$SUPABASE_CALLBACK_URL${NC}"
    echo "       ${GREEN}$LOCAL_CALLBACK_URL${NC}"
    echo "    6. Click 'Create'"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Copy the Client ID and Client Secret immediately!${NC}"
    echo "   The Client Secret is only shown once during creation."
    echo ""
    read -p "Press Enter when OAuth client is created..."

    # Get credentials from user
    echo ""
    echo -e "${BLUE}📋 Enter OAuth Client Credentials${NC}"
    echo ""
    read -p "Client ID: " CLIENT_ID
    read -p "Client Secret: " CLIENT_SECRET

    # Validate Client ID format
    if [[ -n "$CLIENT_ID" && ! "$CLIENT_ID" =~ \.googleusercontent\.com$ ]]; then
        echo -e "${YELLOW}⚠️  Warning: CLIENT_ID format looks incorrect${NC}"
        echo "  Expected format: *.googleusercontent.com"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    # Validate Client Secret format (basic check)
    if [[ -n "$CLIENT_SECRET" && ! "$CLIENT_SECRET" =~ ^GOCSPX- ]]; then
        echo -e "${YELLOW}⚠️  Warning: CLIENT_SECRET format looks unusual${NC}"
        echo "  Expected format: GOCSPX-*"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Validate inputs
if [ -z "$CLIENT_ID" ] || [ -z "$CLIENT_SECRET" ]; then
    echo -e "${RED}❌ Client ID and Client Secret are required${NC}"
    exit 1
fi

# Output credentials
echo ""
echo -e "${GREEN}✅ OAuth client configured successfully!${NC}"
echo ""
echo -e "${YELLOW}⚠️  SECURITY WARNING: Credentials will be displayed below.${NC}"
echo -e "${YELLOW}    Consider clearing terminal history after copying if needed.${NC}"
echo ""
read -p "Press Enter to display credentials..."
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📝 Next Steps: Configure Supabase${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "1. Go to Supabase Dashboard:"
echo "   https://supabase.com/dashboard/project/$SUPABASE_PROJECT_ID/auth/providers"
echo ""
echo "2. Find 'Google' in the providers list and click to configure"
echo ""
echo "3. Enable the provider and enter:"
echo ""
echo -e "   ${GREEN}Client ID:${NC}"
echo "   $CLIENT_ID"
echo ""
echo -e "   ${GREEN}Client Secret:${NC}"
echo "   $CLIENT_SECRET"
echo ""
echo "4. Click 'Save'"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📋 Credentials Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Google Cloud Project: $PROJECT_ID"
echo "OAuth Client ID: $CLIENT_ID"
echo "OAuth Client Secret: $CLIENT_SECRET"
echo ""
echo "Supabase Callback URL: $SUPABASE_CALLBACK_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""
echo -e "${YELLOW}⚠️  Keep these credentials secure!${NC}"
echo -e "${YELLOW}⚠️  Never commit Client Secret to git${NC}"
echo -e "${YELLOW}⚠️  Clear terminal history if needed: history -c${NC}"
echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
