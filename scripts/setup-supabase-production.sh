#!/bin/bash
# Setup Supabase secrets in Google Cloud for production deployment
# Run this script to configure Cloud Run with Supabase credentials

set -e

PROJECT_ID="kinemotion-backend"
SUPABASE_URL="https://smutfsalcbnfveqijttb.supabase.co"
SUPABASE_ANON_KEY="sb_publishable_WMMkJVB5hpNdZlyWykxDRg_uvW1lqPN"
SERVICE_ACCOUNT="github-actions-deploy@kinemotion-backend.iam.gserviceaccount.com"

echo "🔐 Setting up Supabase secrets in Google Cloud..."
echo ""
echo "Project: $PROJECT_ID"
echo "Supabase URL: $SUPABASE_URL"
echo ""

# Check if secrets already exist
echo "Checking for existing secrets..."

if gcloud secrets describe SUPABASE_URL --project=$PROJECT_ID &>/dev/null; then
    echo "⚠️  SUPABASE_URL secret already exists"
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -n "$SUPABASE_URL" | gcloud secrets versions add SUPABASE_URL --data-file=- --project=$PROJECT_ID
        echo "✅ Updated SUPABASE_URL"
    fi
else
    echo "Creating SUPABASE_URL secret..."
    echo -n "$SUPABASE_URL" | gcloud secrets create SUPABASE_URL --data-file=- --project=$PROJECT_ID
    echo "✅ Created SUPABASE_URL"
fi

if gcloud secrets describe SUPABASE_ANON_KEY --project=$PROJECT_ID &>/dev/null; then
    echo "⚠️  SUPABASE_ANON_KEY secret already exists"
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -n "$SUPABASE_ANON_KEY" | gcloud secrets versions add SUPABASE_ANON_KEY --data-file=- --project=$PROJECT_ID
        echo "✅ Updated SUPABASE_ANON_KEY"
    fi
else
    echo "Creating SUPABASE_ANON_KEY secret..."
    echo -n "$SUPABASE_ANON_KEY" | gcloud secrets create SUPABASE_ANON_KEY --data-file=- --project=$PROJECT_ID
    echo "✅ Created SUPABASE_ANON_KEY"
fi

echo ""
echo "🔑 Granting secret access to service account..."
echo "Service account: $SERVICE_ACCOUNT"
echo ""

# Grant access to SUPABASE_URL
gcloud secrets add-iam-policy-binding SUPABASE_URL \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor" \
  --project=$PROJECT_ID \
  --quiet

echo "✅ Granted access to SUPABASE_URL"

# Grant access to SUPABASE_ANON_KEY
gcloud secrets add-iam-policy-binding SUPABASE_ANON_KEY \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor" \
  --project=$PROJECT_ID \
  --quiet

echo "✅ Granted access to SUPABASE_ANON_KEY"

echo ""
echo "🎉 Secrets configured successfully!"
echo ""
echo "Next steps:"
echo "1. Update .github/workflows/deploy-backend.yml with the deployment flags"
echo "2. Commit and push to trigger deployment"
echo "3. Configure Vercel environment variables:"
echo "   - VITE_SUPABASE_URL: $SUPABASE_URL"
echo "   - VITE_SUPABASE_ANON_KEY: $SUPABASE_ANON_KEY"
echo "   - VITE_API_URL: https://kinemotion-backend-1008251132682.us-central1.run.app"
