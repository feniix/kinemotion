#!/bin/bash
set -euo pipefail

# Setup Workload Identity Federation for GitHub Actions → Cloud Run deployment
# This script is idempotent - safe to run multiple times

PROJECT_ID="kinemotion-backend"
REPO="feniix/kinemotion"
SERVICE_ACCOUNT_NAME="github-actions-deploy"
POOL_NAME="github-pool"
PROVIDER_NAME="github-provider"

echo "🔧 Setting up Workload Identity Federation for GitHub Actions"
echo "Project: $PROJECT_ID"
echo "Repository: $REPO"
echo ""

# Get project number
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
echo "✓ Project number: $PROJECT_NUMBER"

# Enable required APIs
echo ""
echo "📦 Enabling required APIs..."
gcloud services enable \
  iamcredentials.googleapis.com \
  cloudresourcemanager.googleapis.com \
  sts.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  containerregistry.googleapis.com \
  storage-component.googleapis.com \
  secretmanager.googleapis.com \
  --project="$PROJECT_ID" 2>/dev/null || echo "  APIs already enabled"

# Create Workload Identity Pool (idempotent)
echo ""
echo "🏊 Creating Workload Identity Pool..."
if gcloud iam workload-identity-pools describe "$POOL_NAME" \
  --location="global" \
  --project="$PROJECT_ID" &>/dev/null; then
  echo "  ✓ Pool '$POOL_NAME' already exists"
else
  gcloud iam workload-identity-pools create "$POOL_NAME" \
    --location="global" \
    --display-name="GitHub Actions Pool" \
    --project="$PROJECT_ID"
  echo "  ✓ Created pool '$POOL_NAME'"
fi

# Create Workload Identity Provider (idempotent)
echo ""
echo "🔑 Creating GitHub OIDC Provider..."
if gcloud iam workload-identity-pools providers describe "$PROVIDER_NAME" \
  --location="global" \
  --workload-identity-pool="$POOL_NAME" \
  --project="$PROJECT_ID" &>/dev/null; then
  echo "  ✓ Provider '$PROVIDER_NAME' already exists"
else
  gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_NAME" \
    --location="global" \
    --workload-identity-pool="$POOL_NAME" \
    --display-name="GitHub Provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
    --attribute-condition="assertion.repository_owner=='feniix'" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --project="$PROJECT_ID"
  echo "  ✓ Created provider '$PROVIDER_NAME'"
fi

# Create Service Account (idempotent)
echo ""
echo "👤 Creating Service Account..."
if gcloud iam service-accounts describe "$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --project="$PROJECT_ID" &>/dev/null; then
  echo "  ✓ Service account '$SERVICE_ACCOUNT_NAME' already exists"
else
  gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
    --display-name="GitHub Actions Deployment" \
    --project="$PROJECT_ID"
  echo "  ✓ Created service account '$SERVICE_ACCOUNT_NAME'"
fi

# Grant permissions (idempotent - will show warnings if already exist)
echo ""
echo "🔐 Granting IAM permissions..."

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin" \
  --condition=None 2>/dev/null || echo "  ✓ roles/run.admin already granted"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser" \
  --condition=None 2>/dev/null || echo "  ✓ roles/iam.serviceAccountUser already granted"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin" \
  --condition=None 2>/dev/null || echo "  ✓ roles/storage.admin already granted"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.editor" \
  --condition=None 2>/dev/null || echo "  ✓ roles/cloudbuild.builds.editor already granted"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.reader" \
  --condition=None 2>/dev/null || echo "  ✓ roles/artifactregistry.reader already granted"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/serviceusage.serviceUsageConsumer" \
  --condition=None 2>/dev/null || echo "  ✓ roles/serviceusage.serviceUsageConsumer already granted"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.builder" \
  --condition=None 2>/dev/null || echo "  ✓ roles/cloudbuild.builds.builder already granted"

# NOTE: GitHub Actions deployment account does NOT need secretmanager.secretAccessor
# Only the Cloud Run runtime service account needs it (it runs the container and reads secrets)

echo "  ✓ All required roles granted"

# Create dedicated Cloud Run runtime service account (idempotent)
echo ""
echo "🏃 Creating Cloud Run runtime service account..."
RUNTIME_SERVICE_ACCOUNT_NAME="kinemotion-backend-runtime"
if gcloud iam service-accounts describe "$RUNTIME_SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --project="$PROJECT_ID" &>/dev/null; then
  echo "  ✓ Runtime service account '$RUNTIME_SERVICE_ACCOUNT_NAME' already exists"
else
  gcloud iam service-accounts create "$RUNTIME_SERVICE_ACCOUNT_NAME" \
    --display-name="Kinemotion Backend Runtime" \
    --project="$PROJECT_ID"
  echo "  ✓ Created runtime service account '$RUNTIME_SERVICE_ACCOUNT_NAME'"
fi

# Grant Cloud Run runtime account access to specific secrets (least privilege)
echo ""
echo "🔐 Granting Cloud Run runtime account access to secrets..."
for SECRET in "SUPABASE_URL" "SUPABASE_ANON_KEY"; do
  gcloud secrets add-iam-policy-binding "$SECRET" \
    --member="serviceAccount:$RUNTIME_SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project="$PROJECT_ID" 2>/dev/null || echo "  ✓ $SECRET access already granted"
done

# Allow GitHub to impersonate service account (idempotent)
echo ""
echo "🔗 Binding GitHub repository to service account..."
gcloud iam service-accounts add-iam-policy-binding \
  "$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --project="$PROJECT_ID" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_NAME/attribute.repository/$REPO" \
  2>/dev/null || echo "  ✓ Workload identity binding already exists"

echo ""
echo "✅ Setup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 GitHub Actions deployment credentials (in workflow):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "workload_identity_provider: 'projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_NAME/providers/$PROVIDER_NAME'"
echo "service_account: '$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com'"
echo ""
echo "These values are NOT sensitive and can be committed to your repository."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏃 Cloud Run runtime service account:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "service_account: '$RUNTIME_SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com'"
echo ""
echo "Add this to .github/workflows/deploy-backend.yml deploy step:"
echo "  --service-account=$RUNTIME_SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"
echo ""
echo "This account has least-privilege access to only:"
echo "  - SUPABASE_URL"
echo "  - SUPABASE_ANON_KEY"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Test the setup:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Update .github/workflows/deploy-backend.yml with the values above"
echo "2. Push a change to backend/ or src/kinemotion/"
echo "3. Watch workflow: https://github.com/$REPO/actions"
echo ""
