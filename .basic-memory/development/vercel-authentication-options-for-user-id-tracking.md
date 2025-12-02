---
title: Vercel Authentication Options for User ID Tracking
type: note
permalink: development/vercel-authentication-options-for-user-id-tracking-1
---

# Vercel Authentication Options for User ID Tracking

## Problem Statement

Need to log authenticated user IDs in the backend, but Vercel Deployment Protection (Vercel Authentication) **does NOT** provide user identity information to backend applications.

## Vercel Authentication Options

### Option 1: Sign in with Vercel (OAuth)
**Use Case:** Full user authentication with user profile access

**How it works:**
- Implements OAuth 2.0 / OIDC flow
- Users sign in with their Vercel account
- Backend receives access tokens with user information
- Can query Vercel API for user details (ID, email, name, team)

**Implementation:**
```typescript
// Frontend initiates OAuth flow
window.location.href = 'https://vercel.com/oauth/authorize?' +
  'client_id=YOUR_CLIENT_ID&' +
  'redirect_uri=YOUR_CALLBACK&' +
  'response_type=code&' +
  'scope=user:email'

// Backend exchanges code for token
const response = await fetch('https://api.vercel.com/login/oauth/token', {
  method: 'POST',
  body: JSON.stringify({
    client_id: process.env.VERCEL_CLIENT_ID,
    client_secret: process.env.VERCEL_CLIENT_SECRET,
    code: authCode,
  }),
})

// Get user info
const userInfo = await fetch('https://api.vercel.com/login/oauth/userinfo', {
  headers: { Authorization: `Bearer ${accessToken}` }
})
```

**Pros:**
- ✅ Full user identity (ID, email, name, avatar)
- ✅ No separate user management needed
- ✅ OAuth 2.0 standard
- ✅ Can access Vercel API on behalf of user

**Cons:**
- ❌ Requires OAuth setup in Vercel dashboard
- ❌ Frontend must handle OAuth flow
- ❌ More complex than simple header extraction

**Documentation:** https://vercel.com/docs/sign-in-with-vercel

---

### Option 2: Vercel OIDC Tokens (for Vercel Functions)
**Use Case:** Backend-to-backend authentication from Vercel Functions

**How it works:**
- Vercel automatically generates OIDC tokens for Functions
- Tokens are cryptographically signed by Vercel
- Can be validated by your own API or other cloud providers
- Contains deployment metadata (not end-user identity)

**Implementation:**
```typescript
// In Vercel Function
import { getwaitUntil } from '@vercel/functions'

export async function GET(request: Request) {
  const token = await getToken({
    url: process.env.VERCEL_URL,
  })

  // Send token to your API
  const response = await fetch('https://your-api.com/analyze', {
    headers: { Authorization: `Bearer ${token}` }
  })
}

// In your backend API
import * as jose from 'jose'

const JWKS = jose.createRemoteJWKSet(
  new URL('https://oidc.vercel.com/.well-known/jwks')
)

const { payload } = await jose.jwtVerify(token, JWKS, {
  issuer: 'https://oidc.vercel.com',
  audience: process.env.VERCEL_URL,
})

// payload contains: iss, aud, sub (deployment ID), iat, exp
```

**Pros:**
- ✅ No configuration needed (automatic)
- ✅ Cryptographically secure
- ✅ Works with cloud providers (AWS, GCP, Azure)

**Cons:**
- ❌ Only available in Vercel Functions (not standalone backends)
- ❌ Contains deployment identity, NOT end-user identity
- ❌ Not suitable for tracking which human user made requests

**Documentation:** https://vercel.com/docs/oidc

---

### Option 3: Third-Party Authentication (Clerk, Auth0, Supabase, etc.)
**Use Case:** Production-grade user authentication with full control

**Recommended for:** Applications that need:
- User sign-up and login
- Multiple authentication methods (email, social, etc.)
- User management dashboard
- Role-based access control

**Popular Options:**
- **Clerk:** Best developer experience, Vercel-optimized
- **Auth0:** Enterprise-grade, highly customizable
- **Supabase Auth:** Open source, includes database
- **Firebase Auth:** Google ecosystem, generous free tier

**Example with Clerk:**
```typescript
// Frontend (automatic)
import { SignIn, useUser } from '@clerk/nextjs'

function App() {
  const { user } = useUser()
  // Clerk automatically includes auth token in requests
}

// Backend
from clerk_backend_api import Clerk

clerk = Clerk(bearer_auth=os.environ.get("CLERK_SECRET_KEY"))

def get_user_from_token(auth_header: str):
    token = auth_header.replace("Bearer ", "")
    user = clerk.users.get_user(token)
    return user.id
```

**Pros:**
- ✅ Production-ready user management
- ✅ Multiple auth methods
- ✅ User dashboards and admin panels
- ✅ SDKs for most frameworks

**Cons:**
- ❌ Additional service dependency
- ❌ Costs money at scale
- ❌ Vendor lock-in

---

## Decision Matrix

| Feature | Deployment Protection | Sign in with Vercel | OIDC Tokens | Third-Party Auth |
|---------|----------------------|---------------------|-------------|------------------|
| **Protects deployments** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Provides user ID** | ❌ No | ✅ Yes | ⚠️ Deployment ID only | ✅ Yes |
| **No extra setup** | ✅ Yes | ⚠️ OAuth setup | ✅ Yes | ❌ No |
| **Works standalone backend** | N/A | ✅ Yes | ❌ No | ✅ Yes |
| **Production-ready** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Cost** | Free | Free | Free | $$ |

## Recommendation for Kinemotion

Based on the requirements:

1. **If users need accounts** → Use **Clerk** or **Supabase Auth**
   - Best UX for coaches/athletes
   - Can track usage per user
   - Enables future features (saved videos, history, teams)

2. **If you just need to know "who from Vercel team"** → Use **Sign in with Vercel**
   - Quick setup
   - Good for internal tools
   - Limited to Vercel users only

3. **If backend is on Fly.io** (current setup) → **Cannot use OIDC tokens**
   - OIDC only works for Vercel Functions
   - Backend on Fly.io needs OAuth or third-party auth

## Next Steps

**Question for user:** Which authentication approach do you want to implement?

A. **Sign in with Vercel** (OAuth) - Quick, Vercel users only
B. **Clerk / Auth0 / Supabase** - Full user management
C. **Something else** - Please clarify

Once decided, I can implement:
1. Frontend auth integration
2. Backend token validation
3. Structured logging with user IDs
4. Middleware for request tracking

---

**References:**
- Vercel Sign in: https://vercel.com/docs/sign-in-with-vercel
- Vercel OIDC: https://vercel.com/docs/oidc
- Vercel Deployment Protection: https://vercel.com/docs/deployment-protection
- Clerk: https://clerk.com/docs
- Auth0: https://auth0.com/docs
- Supabase Auth: https://supabase.com/docs/guides/auth
