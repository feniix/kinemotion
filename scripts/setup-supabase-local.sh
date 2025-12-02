#!/bin/bash
# Setup script for Kinemotion with Supabase authentication
# Run this script to configure your local environment

set -e

echo "🔧 Setting up Kinemotion with Supabase authentication..."
echo ""

# Frontend environment
echo "📦 Creating frontend/.env.local..."
cat > frontend/.env.local << 'EOF'
# Supabase Configuration
VITE_SUPABASE_URL=https://smutfsalcbnfveqijttb.supabase.co
VITE_SUPABASE_ANON_KEY=sb_publishable_WMMkJVB5hpNdZlyWykxDRg_uvW1lqPN

# Backend API URL (use Cloud Run URL for production testing)
VITE_API_URL=http://localhost:8000
EOF

echo "✅ Frontend environment configured"
echo ""

# Backend environment
echo "📦 Creating backend/.env..."
cat > backend/.env << 'EOF'
# Supabase Configuration
SUPABASE_URL=https://smutfsalcbnfveqijttb.supabase.co
SUPABASE_ANON_KEY=sb_publishable_WMMkJVB5hpNdZlyWykxDRg_uvW1lqPN

# Logging Configuration
LOG_LEVEL=INFO
JSON_LOGS=false
EOF

echo "✅ Backend environment configured"
echo ""

echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure Supabase redirect URLs:"
echo "   - Go to: https://supabase.com/dashboard/project/smutfsalcbnfveqijttb/auth/url-configuration"
echo "   - Site URL: https://kinemotion.vercel.app"
echo "   - Redirect URLs: https://kinemotion.vercel.app/** and http://localhost:5173/**"
echo ""
echo "2. Start the backend:"
echo "   cd backend && uv run uvicorn kinemotion_backend.app:app --reload"
echo ""
echo "3. Start the frontend:"
echo "   cd frontend && yarn dev"
echo ""
echo "4. Test locally at http://localhost:5173"
