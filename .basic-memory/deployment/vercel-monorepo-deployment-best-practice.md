---
title: Vercel Monorepo Deployment Best Practice
type: note
permalink: deployment/vercel-monorepo-deployment-best-practice
tags:
- vercel
- deployment
- monorepo
- best-practice
---

# Vercel Monorepo Deployment: Best Practice

## Problem
When deploying a monorepo to Vercel where only one subdirectory (e.g., `frontend/`) needs to be deployed, many developers try to use custom `vercel.json` configurations with complex build commands or build scripts. This is unnecessary and violates Vercel's schema.

## Solution: Use Vercel Dashboard Root Directory Setting

**The official, recommended approach from Vercel:**

1. **In Vercel Dashboard**, go to your project → **Settings** → **General**
2. Find **Root Directory** setting
3. Set it to: `frontend/` (or your app's directory)
4. Save

**That's it.** Vercel will:
- Auto-detect `package.json` in `frontend/`
- Auto-detect the framework (Vite, Next.js, etc.)
- Auto-run the appropriate build command (`yarn build`, `npm run build`, etc.)
- Auto-detect output directory (`dist/`, `.next/`, etc.)

## Why This is Better

| Approach | Complexity | Reliability | Maintainability |
|----------|-----------|-------------|-----------------|
| Root Directory setting | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Custom vercel.json | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| Build scripts | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |

## When to Use vercel.json

Only use `vercel.json` for:
- True monorepos with yarn workspaces (use Vercel's official examples)
- Complex environment variable handling
- Custom routing or middleware

For simple cases where one directory has its own package.json: **Always use Root Directory setting.**

## References
- [Vercel Monorepos Official Documentation](https://vercel.com/docs/monorepos)
- [Deploying Yarn Monorepos to Vercel](https://examples.vercel.com/guides/deploying-yarn-monorepos-to-vercel)
- [Vercel Monorepo FAQ](https://vercel.com/docs/monorepos/monorepo-faq)
