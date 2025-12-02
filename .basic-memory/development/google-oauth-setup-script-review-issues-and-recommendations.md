---
title: Google OAuth Setup Script Review - Issues and Recommendations
type: note
permalink: development/google-oauth-setup-script-review-issues-and-recommendations-1
---

# Google OAuth Setup Script Review

## Script: `scripts/setup-google-oauth.sh`

**Review Date:** 2025-12-02
**Review Method:** code-reasoning, ref, exa, serena, basic-memory

## Critical Issues Found

### 1. ❌ Incorrect OAuth Consent Screen Check
**Location:** Lines 107-112
**Issue:** Uses `gcloud iap oauth-brands list` to check OAuth consent screen configuration. IAP (Identity-Aware Proxy) brands are different from OAuth consent screen. This check is unreliable and may give false positives/negatives.

**Fix:** Remove automated check, use user prompt: "Is OAuth consent screen already configured? (y/n)"

### 2. ❌ Unnecessary API Enabled
**Location:** Line 93
**Issue:** Enables `iap.googleapis.com` which is for Identity-Aware Proxy, not needed for standard OAuth clients used with Supabase.

**Fix:** Remove `iap.googleapis.com` from the API list. Only `cloudresourcemanager.googleapis.com` is needed for project operations.

### 3. ⚠️ Error Handling Pattern
**Location:** Line 94
**Issue:** Uses `2>/dev/null || echo` which suppresses errors. With `set -e`, if gcloud fails before the `||`, script exits. Pattern works but hides useful error messages.

**Fix:** Use `gcloud services enable ... || true` or wrap in conditional:
```bash
if ! gcloud services enable ... 2>&1; then
    echo "  APIs already enabled or error occurred"
fi
```

## Medium Priority Issues

### 4. ⚠️ CLIENT_SECRET Validation Logic
**Location:** Lines 185, 249
**Issue:** Allows empty CLIENT_SECRET on line 185 but requires it on line 249. Logic flow is correct (offers to create new if missing), but error message could be clearer.

**Fix:** Improve error message: "CLIENT_SECRET is required for Supabase configuration. If you don't have it, please create a new OAuth client."

### 5. ⚠️ Missing Input Validation
**Location:** Lines 83, 179, 244
**Issue:** No format validation for:
- SUPABASE_PROJECT_ID (should be alphanumeric, ~20 chars)
- CLIENT_ID (should end with `.googleusercontent.com`)
- CLIENT_SECRET (should start with `GOCSPX-`)

**Fix:** Add basic format checks:
```bash
if [[ ! "$CLIENT_ID" =~ \.googleusercontent\.com$ ]]; then
    echo "Warning: CLIENT_ID format looks incorrect"
fi
```

### 6. ⚠️ Security: Credentials in stdout
**Location:** Lines 270, 273
**Issue:** CLIENT_SECRET printed to stdout, could be logged in terminal history or scrollback.

**Fix:** Add warning: "⚠️  Credentials will be displayed. Clear terminal history after copying if needed."

## Minor Issues

### 7. ℹ️ Unused Variable
**Location:** Line 103
**Issue:** PROJECT_NUMBER is calculated but only used for IAP check (which is incorrect anyway).

**Fix:** Remove PROJECT_NUMBER if removing IAP check, or use it for other purposes.

### 8. ℹ️ Misleading Comment
**Location:** Lines 101-102
**Issue:** Comment says "checking for OAuth clients" but code checks IAP brands.

**Fix:** Update comment or remove if fixing issue #1.

## What's Good ✅

1. ✅ Proper use of `set -euo pipefail` for error handling
2. ✅ Idempotent design - allows skipping steps
3. ✅ Clear user guidance and instructions
4. ✅ Environment variable support for configuration
5. ✅ Browser auto-open feature (macOS/Linux)
6. ✅ Good error messages and security warnings
7. ✅ Follows project's script patterns (similar to setup-github-deploy.sh)

## Recommendations

### High Priority
1. Fix OAuth consent screen check (remove IAP-based check)
2. Remove unnecessary `iap.googleapis.com` API
3. Improve error handling for API enabling

### Medium Priority
4. Add input format validation
5. Improve CLIENT_SECRET handling error messages
6. Add security warning about terminal history

### Low Priority
7. Clean up unused variables
8. Update misleading comments

## Comparison with Similar Scripts

**setup-github-deploy.sh:**
- Uses same API enabling pattern (`2>/dev/null || echo`)
- Properly idempotent with existence checks
- Good pattern to follow for error handling

**setup-supabase-production.sh:**
- Uses `gcloud secrets` commands (different use case)
- Good pattern for handling existing resources

## Testing Recommendations

1. Test with existing OAuth consent screen configured
2. Test with existing OAuth client
3. Test with missing CLIENT_SECRET
4. Test error cases (invalid project ID, etc.)
5. Test idempotency (run script twice)

## References

- Google Cloud OAuth Setup: https://cloud.google.com/iam/docs/workforce-manage-oauth-app
- Bash Error Handling: https://vaneyckt.io/posts/safer_bash_scripts_with_set_euxo_pipefail/
- Project Script Patterns: `scripts/setup-github-deploy.sh`
