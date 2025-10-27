# Railway Deployment Plan for Unified MCP Server

## Overview

This document provides deployment instructions for the **Unified MCP Server** that combines both Pizzaz and Solar System widgets in a single Railway service.

## Project Architecture

The repository contains:
- **Frontend widgets**: React components that render in ChatGPT (built to `assets/`)
- **Pizzaz MCP Server** (Python): Multiple pizza-themed widget tools
- **Solar System MCP Server** (Python): 3D interactive solar system viewer
- **Unified Server** (`unified_server.py`): Combines both MCP servers with static asset serving

## Deployment Strategy

### Single Unified Service (Implemented)

The unified server approach combines both MCP servers under one Railway service:
- Serves static assets at `/assets/`
- Exposes Pizzaz MCP at `/pizzaz/mcp`
- Exposes Solar System MCP at `/solar/mcp`
- Includes health check at `/health`
- Simplifies deployment and reduces costs

---

## Phase 1: Pre-Deployment Preparation

### Step 1.1: Build Widget Assets

The widget JavaScript/CSS bundles must be built before deployment:

```bash
# Install dependencies
pnpm install

# Build all widgets (generates versioned files in assets/)
pnpm run build
```

**Expected output in `assets/`:**
- `pizzaz-[hash].html/js/css`
- `pizzaz-carousel-[hash].html/js/css`
- `pizzaz-list-[hash].html/js/css`
- `pizzaz-albums-[hash].html/js/css`
- `solar-system-[hash].html/js/css`

### Step 1.2: Host Widget Assets

**Critical**: The widget HTML files must be publicly accessible via HTTPS. Railway can host these, or you can use a CDN.

**Current issue**: MCP servers reference `https://persistent.oaistatic.com/ecosystem-built-assets/`, which are OpenAI's hosted assets. You'll need to either:

**Option A**: Host on Railway static service
**Option B**: Upload to a CDN (Cloudflare R2, AWS S3, etc.)
**Option C**: Use Railway's static file serving

### Step 1.3: Update Asset URLs

After hosting assets, update the MCP server code to reference your deployed URLs:

**In `pizzaz_server_python/main.py`** (lines 41-44, etc.):
```python
html=(
    "<div id=\"pizzaz-root\"></div>\n"
    "<link rel=\"stylesheet\" href=\"https://YOUR-RAILWAY-URL.railway.app/assets/pizzaz-[hash].css\">\n"
    "<script type=\"module\" src=\"https://YOUR-RAILWAY-URL.railway.app/assets/pizzaz-[hash].js\"></script>"
),
```

**In `solar-system_server_python/main.py`** (lines 66-70):
```python
html=(
    "<div id=\"solar-system-root\"></div>\n"
    "<link rel=\"stylesheet\" href=\"https://YOUR-RAILWAY-URL.railway.app/assets/solar-system-[hash].css\">\n"
    "<script type=\"module\" src=\"https://YOUR-RAILWAY-URL.railway.app/assets/solar-system-[hash].js\"></script>"
),
```

---

## Phase 2: Railway Configuration Files

The following configuration files have been created in the repository:

### `railway.json`
Configured to run the unified server with uvicorn:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn unified_server:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### `nixpacks.toml`
Build configuration that installs dependencies and builds assets:
```toml
[phases.setup]
nixPkgs = ["python312", "nodejs-18_x", "pnpm"]

[phases.install]
cmds = [
  "pnpm install",
  "pip install -r pizzaz_server_python/requirements.txt",
  "pip install -r solar-system_server_python/requirements.txt",
  "pip install python-dotenv"
]

[phases.build]
cmds = ["pnpm run build"]

[start]
cmd = "uvicorn unified_server:app --host 0.0.0.0 --port $PORT"
```

---

## Phase 3: Railway Deployment

### Deploy the Unified Server

1. **Push code to GitHub**:
   ```bash
   git add .
   git commit -m "Add unified MCP server for Railway deployment"
   git push origin main
   ```

2. **Create Railway project**:
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose this repository

3. **Set environment variable**:
   - After deployment, go to project settings
   - Add environment variable `STATIC_URL` with value `https://YOUR-PROJECT.railway.app`
   - Railway will auto-generate the URL

4. **Deploy**:
   - Railway will automatically detect `nixpacks.toml` and `railway.json`
   - The build will:
     - Install Node.js dependencies with pnpm
     - Build widget assets
     - Install Python dependencies
     - Start the unified server

5. **Get your Railway URL**:
   - Visit your Railway project dashboard
   - Copy the public URL (e.g., `your-project-production.up.railway.app`)

---

## Phase 4: Connect to ChatGPT

### Enable Developer Mode

1. Go to ChatGPT Settings
2. Enable "Developer mode"
3. Navigate to Settings > Connectors

### Add Pizzaz Connector

1. Click "Add Connector"
2. **Name**: "Pizzaz Widgets"
3. **URL**: `https://YOUR-RAILWAY-URL.railway.app/pizzaz/mcp`
4. **Type**: Model Context Protocol (MCP)
5. Save and enable

### Add Solar System Connector

1. Click "Add Connector"
2. **Name**: "Solar System Viewer"
3. **URL**: `https://YOUR-RAILWAY-URL.railway.app/solar/mcp`
4. **Type**: Model Context Protocol (MCP)
5. Save and enable

---

## Phase 5: Testing in ChatGPT

### Test Pizzaz Widgets

**Test prompts**:
- "Show me a pizza map with pepperoni"
- "Create a pizza carousel with mushrooms"
- "Display a pizza album with olives"
- "Show me a pizza list with pineapple"

**Expected behavior**:
- ChatGPT calls the appropriate MCP tool
- Widget HTML is rendered inline
- Interactive map/carousel/album appears

### Test Solar System Widget

**Test prompts**:
- "Show me the solar system focused on Mars"
- "Display Jupiter in the solar system"
- "Explore Earth in the solar system viewer"

**Expected behavior**:
- 3D solar system widget renders
- Camera focuses on requested planet
- Interactive 3D controls work

---

## Phase 6: Testing and Troubleshooting

### Common Issues

#### Issue 1: CORS Errors
**Symptom**: Widget fails to load in ChatGPT
**Solution**: Verify CORS middleware is enabled in both Python servers (already present in code)

#### Issue 2: Assets 404
**Symptom**: Widget HTML loads but JS/CSS missing
**Solution**:
- Check static assets server is running
- Verify asset URLs in MCP server code are correct
- Ensure assets were built correctly

#### Issue 3: MCP Connection Failed
**Symptom**: ChatGPT can't connect to MCP server
**Solution**:
- Verify Railway service is running
- Check `/mcp` endpoint responds: `curl https://your-url.railway.app/mcp`
- Review Railway logs for errors

#### Issue 4: Widget Not Rendering
**Symptom**: Tool executes but no widget appears
**Solution**:
- Verify `_meta` fields are present in tool response
- Check `openai/outputTemplate` URI is correct
- Ensure widget HTML is accessible publicly

#### Issue 5: Build Fails on Railway
**Symptom**: Deployment fails during build
**Solution**:
- Check Python version compatibility (Python 3.12)
- Verify all dependencies in requirements.txt files
- Review Railway build logs for specific errors

---

## Deployment Checklist

- [x] Build widget assets (`pnpm run build`)
- [x] Create unified_server.py
- [x] Update asset URLs to use environment variables
- [x] Create railway.json and nixpacks.toml
- [ ] Push to GitHub
- [ ] Create Railway project
- [ ] Set STATIC_URL environment variable
- [ ] Deploy to Railway
- [ ] Test `/health`, `/pizzaz/mcp`, and `/solar/mcp` endpoints
- [ ] Add connectors to ChatGPT
- [ ] Test widgets in ChatGPT

---

## Quick Start Summary

```bash
# 1. Build assets (already done)
pnpm run build

# 2. Push to GitHub
git add .
git commit -m "Add unified MCP server for Railway deployment"
git push origin main

# 3. Create Railway project at railway.app
# - Connect your GitHub repository
# - Set environment variable: STATIC_URL=https://YOUR-URL.railway.app
# - Deploy

# 4. Test endpoints
curl https://your-url.railway.app/health
curl https://your-url.railway.app/pizzaz/mcp
curl https://your-url.railway.app/solar/mcp

# 5. Add connectors to ChatGPT Settings > Developer Mode > Connectors
# - Pizzaz Widgets: https://your-url.railway.app/pizzaz/mcp
# - Solar System Viewer: https://your-url.railway.app/solar/mcp

# 6. Test in ChatGPT
# "Show me a pizza map with pepperoni"
# "Display Jupiter in the solar system"
```

---

## Support Resources

- **Railway Docs**: https://docs.railway.app/
- **MCP Specification**: https://modelcontextprotocol.io/
- **ChatGPT Developer Mode**: https://platform.openai.com/docs/guides/developer-mode
- **FastAPI Docs**: https://fastapi.tiangolo.com/
