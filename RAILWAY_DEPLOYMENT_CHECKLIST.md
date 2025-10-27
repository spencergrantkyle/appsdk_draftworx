# Railway GitHub Deployment Checklist

## Overview

This document provides a comprehensive checklist to ensure your repository is properly configured for Railway deployment from GitHub. Based on Railway's requirements and analysis of the current repository.

---

## Current Status

**Repository**: `spencergrantkyle/appsdk_draftworx`  
**Project**: appsdk-mcp-server  
**Deployment URL**: https://appsdk-mcp-server-production.up.railway.app  
**Status**: Initial deployment failed - configuration required

---

## Railway Requirements for GitHub Deployment

### Essential Files ✅ (Already Present)

1. **railway.json** ✅
   - Status: Present in repository
   - Purpose: Railway project configuration
   - Location: Repository root
   - Note: Specifies NIXPACKS builder and start command

2. **nixpacks.toml** ✅
   - Status: Present in repository
   - Purpose: Custom build configuration for multi-runtime deployment
   - Location: Repository root
   - Note: Configures Python 3.12, Node.js, and build steps

3. **requirements.txt** ✅
   - Status: Present in both server directories
   - Locations:
     - `pizzaz_server_python/requirements.txt`
     - `solar-system_server_python/requirements.txt`
   - Note: Lists Python dependencies for MCP servers

4. **package.json** ✅
   - Status: Present in root
   - Purpose: Node.js dependencies and build scripts
   - Note: Contains pnpm workspace configuration

5. **pnpm-workspace.yaml** ✅
   - Status: Present
   - Purpose: Monorepo workspace configuration

---

## Issues Identified in Current Configuration

### Critical Issues

#### 1. **Unified Dependencies File Missing**
- **Issue**: `requirements-unified.txt` exists but may not include all dependencies
- **Problem**: Railway needs a single source of truth for Python dependencies
- **Solution Required**: Create comprehensive requirements file or use proper path

#### 2. **Nixpacks Configuration Needs Adjustment**
- **Current Issue**: The `nixpacks.toml` installs dependencies from subdirectories
- **Railway Expectation**: Dependencies should be installable from the root context
- **Solution Required**: Modify install commands or create root-level requirements.txt

#### 3. **Assets Directory Status**
- **Issue**: Built assets are in the repository but may not be included in Railway build
- **Current State**: Assets exist (pizzaz-2d2b.*, solar-system-2d2b.*, etc.)
- **Concern**: Build process creates assets during Railway deployment, not using pre-built ones

#### 4. **Port Configuration**
- **Issue**: Application must listen on `$PORT` environment variable
- **Status**: ✅ Configured correctly in railway.json start command

---

## Step-by-Step Fix Process

### Phase 1: Repository Structure Verification

**Step 1.1: Verify Essential Files Are Tracked**
```bash
# Run this command to confirm:
git ls-files | grep -E '(railway\.json|nixpacks\.toml|package\.json)'

# Expected output:
railway.json
nixpacks.toml
package.json
```

**Step 1.2: Check Assets Directory**
```bash
# Verify built assets exist:
ls -la assets/ | grep -E '(pizzaz|solar-system)'

# Should show:
# pizzaz-2d2b.css/js/html
# solar-system-2d2b.css/js/html
```

**Step 1.3: Verify Python Requirements Files**
```bash
# Check all requirements.txt files:
find . -name "requirements.txt" -not -path "./venv/*" -not -path "./node_modules/*"

# Should show:
# ./pizzaz_server_python/requirements.txt
# ./solar-system_server_python/requirements.txt
```

---

### Phase 2: Configuration File Updates

#### Fix 1: Create Root-Level Python Requirements

**Create `requirements.txt` in repository root:**

```txt
# Core MCP dependencies
mcp[fastapi]>=0.1.0
fastapi>=0.115.0
uvicorn>=0.30.0
python-dotenv>=1.0.0
pydantic>=2.0.0
starlette>=0.40.0
```

**Why**: Railway's Nixpacks looks for `requirements.txt` in the root. While your servers have their own, we need a unified approach.

#### Fix 2: Update nixpacks.toml

**Current Configuration Issues:**
```toml
[phases.install]
cmds = [
  "pnpm install",
  "pip install -r pizzaz_server_python/requirements.txt",
  "pip install -r solar-system_server_python/requirements.txt",
  "pip install python-dotenv"
]
```

**Problem**: Installing dependencies separately may cause version conflicts

**Proposed Fix:**

```toml
[phases.setup]
nixPkgs = ["python312", "nodejs-18_x", "pnpm"]

[phases.install]
# Install Node.js dependencies first
cmds = [
  "echo 'Installing Node.js dependencies...'",
  "pnpm install"
]

# Build assets
cmds = [
  "echo 'Building widget assets...'",
  "pnpm run build"
]

# Install Python dependencies
cmds = [
  "echo 'Installing Python dependencies...'",
  "pip install --upgrade pip",
  "pip install -r pizzaz_server_python/requirements.txt",
  "pip install -r solar-system_server_python/requirements.txt"
]
```

**Alternative Simpler Approach:**

Create a single `requirements.txt` with combined dependencies:

```toml
[phases.setup]
nixPkgs = ["python312", "nodejs-18_x", "pnpm"]

[phases.install]
cmds = [
  "pnpm install",
  "pnpm run build"
]

[phases.build]
# Python deps will be auto-detected from requirements.txt in subdirs
cmds = [
  "pip install --upgrade pip",
  "pip install -r pizzaz_server_python/requirements.txt",
  "pip install -r solar-system_server_python/requirements.txt"
]

[start]
cmd = "uvicorn unified_server:app --host 0.0.0.0 --port $PORT"
```

#### Fix 3: Update railway.json

**Current Configuration:** ✅ Mostly correct

**Potential Enhancement:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "dockerfilePath": null,
    "nixpacksConfigPath": "nixpacks.toml"
  },
  "deploy": {
    "startCommand": "uvicorn unified_server:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### Fix 4: Environment Variable Configuration

**Required Variables:**
- `STATIC_URL` - Must be set to Railway domain after deployment
- `PORT` - Automatically set by Railway (do not set manually)

**Setup Instructions:**
1. After first successful deployment, get the domain
2. Set environment variable: `STATIC_URL=https://appsdk-mcp-server-production.up.railway.app`
3. Redeploy to apply the variable

---

### Phase 3: GitHub Repository Configuration

#### Step 3.1: Ensure All Files Are Committed and Pushed

```bash
# Check what files are staged/uncommitted
git status

# Expected output should show:
# - All configuration files committed
# - assets/ directory committed
# - No modified files (except venv/ which should be in .gitignore)
```

**Files That MUST Be in Repository:**
- ✅ unified_server.py
- ✅ railway.json
- ✅ nixpacks.toml
- ✅ package.json
- ✅ pnpm-workspace.yaml
- ✅ pizzaz_server_python/main.py
- ✅ solar-system_server_python/main.py
- ✅ pizzaz_server_python/requirements.txt
- ✅ solar-system_server_python/requirements.txt
- ✅ src/ (all source files)
- ✅ build-all.mts
- ✅ tailwind.config.ts
- ✅ tsconfig*.json
- ✅ assets/ (built assets)
- ✅ vendor.yml (if applicable)

#### Step 3.2: Verify .gitignore

**Check .gitignore contains:**
```
venv/
node_modules/
.env
*.pyc
__pycache__/
.DS_Store
```

**Critical**: Assets directory SHOULD NOT be in .gitignore - it needs to be deployed

#### Step 3.3: Verify Branch

```bash
# Confirm you're on the branch Railway will deploy from
git branch

# Should show:
# * main
```

**Railway Configuration:**
- In Railway dashboard, verify deployment branch is set to `main`
- Railway will monitor this branch for changes
- Each push triggers automatic deployment

---

### Phase 4: Railway Project Configuration

#### Step 4.1: Link GitHub Repository

**Current Status**: ✅ Repository is linked

**Verify in Railway Dashboard:**
1. Go to https://railway.app/project/515017a7-caac-4cc8-af45-0811b5fe4d27
2. Navigate to "Settings" → "Deployments"
3. Confirm "Source" shows: `spencergrantkyle/appsdk_draftworx`
4. Confirm "Branch" is set to `main`
5. Confirm "Auto Deploy" is enabled

#### Step 4.2: Set Environment Variables

**Variables to Configure:**

1. **STATIC_URL** (Critical - Set after deployment)
   - Value: `https://appsdk-mcp-server-production.up.railway.app`
   - Purpose: Tells MCP servers where to load widget assets from
   - When to set: After initial deployment succeeds

2. **PORT** (Automatically Set)
   - DO NOT set manually
   - Railway injects this automatically
   - Value: Random port between 1024-65535

**How to Set Environment Variables:**

**Via CLI:**
```bash
cd /Users/spencerdraftworx/projects/draftworx-pr
railway variables --set "STATIC_URL=https://appsdk-mcp-server-production.up.railway.app"
```

**Via Web Dashboard:**
1. Go to Railway project dashboard
2. Click on the service
3. Navigate to "Variables" tab
4. Click "New Variable"
5. Enter key: `STATIC_URL`
6. Enter value: Your Railway domain
7. Click "Add"

#### Step 4.3: Domain Configuration

**Current Status**: ✅ Domain created  
**URL**: https://appsdk-mcp-server-production.up.railway.app

**Verify:**
```bash
railway domain
# Should show: appsdk-mcp-server-production.up.railway.app
```

---

### Phase 5: Build Process Analysis

#### What Railway/Nixpacks Will Do

**Detected Runtimes:**
- Node.js 18 (for pnpm and building widgets)
- Python 3.12 (for MCP servers)

**Build Sequence:**

1. **Setup Phase**
   - Install Nixpacks
   - Install nix packages: python312, nodejs-18_x, pnpm

2. **Install Phase**
   - Run: `pnpm install` (installs all npm dependencies)
   - Build assets: `pnpm run build` (creates assets/ directory)
   - Install Python deps: `pip install -r pizzaz_server_python/requirements.txt`
   - Install Python deps: `pip install -r solar-system_server_python/requirements.txt`

3. **Build Phase**
   - Assets are now in `assets/` directory
   - Python dependencies are installed

4. **Start Phase**
   - Execute: `uvicorn unified_server:app --host 0.0.0.0 --port $PORT`
   - Unified server starts, serving both MCP endpoints

**Expected Build Output:**
```
Setting up build environment...
Installing Node.js dependencies...
✓ 489 packages installed
Building widgets...
✓ Built pizzaz
✓ Built pizzaz-carousel
✓ Built pizzaz-list
✓ Built pizzaz-albums
✓ Built solar-system
Installing Python dependencies...
Requirement already satisfied: mcp[fastapi]>=0.1.0
Requirement already satisfied: fastapi>=0.115.0
...
Starting unified server...
```

---

### Phase 6: Deployment Verification Steps

#### Step 6.1: Initial Deployment

**Monitor Deployment:**
```bash
# Watch logs in real-time
railway logs --follow

# Or check status
railway status
```

**What to Look For:**
- ✅ Build completes without errors
- ✅ All dependencies install successfully
- ✅ Assets build successfully
- ✅ Server starts without port errors

**Common Failure Points:**
- ❌ Missing dependencies in requirements.txt
- ❌ Build command fails (pnpm run build errors)
- ❌ Port binding issues
- ❌ Import errors in unified_server.py

#### Step 6.2: Verify Endpoints

**Test Endpoints After Deployment:**

```bash
# Health check
curl https://appsdk-mcp-server-production.up.railway.app/health

# Expected response:
{
  "status": "healthy",
  "services": ["pizzaz-mcp", "solar-system-mcp", "static-assets"],
  "endpoints": {...}
}

# Pizzaz MCP
curl https://appsdk-mcp-server-production.up.railway.app/pizzaz/mcp

# Solar MCP
curl https://appsdk-mcp-server-production.up.railway.app/solar/mcp

# Static assets
curl https://appsdk-mcp-server-production.up.railway.app/assets/pizzaz-2d2b.js

# Expected: JavaScript file content
```

#### Step 6.3: Update STATIC_URL Environment Variable

**After Deployment Succeeds:**

1. Get the deployment URL:
   ```bash
   railway domain
   ```

2. Set the environment variable:
   ```bash
   railway variables --set "STATIC_URL=https://YOUR-DOMAIN.railway.app"
   ```

3. Redeploy to apply changes:
   ```bash
   railway up
   ```

---

### Phase 7: ChatGPT Integration

#### Step 7.1: Connect ChatGPT Connectors

**Pizzaz Widgets Connector:**
1. Open ChatGPT
2. Go to Settings → Developer Mode
3. Navigate to Connectors
4. Click "Add Connector"
5. Name: "Pizzaz Widgets"
6. URL: `https://appsdk-mcp-server-production.up.railway.app/pizzaz/mcp`
7. Type: Model Context Protocol (MCP)
8. Save and enable

**Solar System Viewer Connector:**
1. Click "Add Connector"
2. Name: "Solar System Viewer"
3. URL: `https://appsdk-mcp-server-production.up.railway.app/solar/mcp`
4. Type: Model Context Protocol (MCP)
5. Save and enable

#### Step 7.2: Test in ChatGPT

**Test Prompts:**
```
"Show me a pizza map with pepperoni"
"Display Jupiter in the solar system"
"Create a pizza carousel with mushrooms"
"Show me the solar system focused on Mars"
```

**Expected Behavior:**
- ChatGPT recognizes the tool
- Tool executes successfully
- Widget renders inline in ChatGPT
- Interactive features work

---

## Troubleshooting Guide

### Issue: Build Fails

**Symptoms:**
- Deployment status shows "FAILED"
- Build logs show errors

**Common Causes:**
1. **Missing Dependencies**
   - Solution: Ensure all requirements.txt files are complete
   - Check: pip install errors in logs

2. **Asset Build Failures**
   - Solution: Verify pnpm install succeeds
   - Check: pnpm run build errors

3. **Python Version Issues**
   - Solution: Update nixpacks.toml to use Python 3.12
   - Current: ✅ Already set

4. **Port Binding Issues**
   - Solution: Ensure --host 0.0.0.0 and --port $PORT
   - Current: ✅ Already configured

### Issue: Server Starts But Endpoints Don't Work

**Symptoms:**
- Deployment succeeds but 404 on /health

**Common Causes:**
1. **Wrong Start Command**
   - Check: railway.json startCommand
   - Solution: Verify it's "uvicorn unified_server:app --host 0.0.0.0 --port $PORT"

2. **Import Errors**
   - Check: Logs for Python import errors
   - Solution: Ensure unified_server.py imports exist

### Issue: Widgets Don't Load

**Symptoms:**
- MCP works but widgets don't render

**Common Causes:**
1. **STATIC_URL Not Set**
   - Solution: Set STATIC_URL environment variable
   - Redeploy after setting

2. **Assets 404**
   - Check: Are assets/ files accessible?
   - Solution: Verify assets built during Railway build

3. **CORS Issues**
   - Check: Browser console for CORS errors
   - Solution: CORS is configured in unified_server.py

---

## Complete Checklist

### Pre-Deployment ✅
- [x] Repository is on GitHub
- [x] All configuration files committed
- [x] railway.json exists
- [x] nixpacks.toml exists
- [x] Requirements files exist
- [x] unified_server.py exists
- [x] Assets are built
- [x] Package.json exists
- [ ] .gitignore excludes venv/ and node_modules/ (verify)

### Railway Configuration ✅
- [x] Project created: appsdk-mcp-server
- [x] GitHub repo linked
- [x] Domain created
- [ ] Environment variables set (STATIC_URL)
- [ ] Deployment triggered

### Deployment Process ⏳
- [ ] Build succeeds (currently FAILED)
- [ ] Dependencies install
- [ ] Assets build
- [ ] Server starts
- [ ] Health endpoint responds
- [ ] MCP endpoints respond

### Post-Deployment ⏳
- [ ] STATIC_URL environment variable set
- [ ] Application accessible via domain
- [ ] Static assets load correctly
- [ ] ChatGPT connectors added
- [ ] Widgets render in ChatGPT

---

## Immediate Next Steps

1. **Fix Configuration Issues**
   - Review and update nixpacks.toml if needed
   - Ensure all dependencies are specified

2. **Redeploy**
   ```bash
   railway up
   ```

3. **Monitor Build Logs**
   - Watch for specific error messages
   - Identify failing step

4. **Set Environment Variables**
   - After successful deployment
   - Set STATIC_URL to Railway domain

5. **Test Endpoints**
   - Verify all endpoints respond
   - Confirm widgets load

6. **Connect to ChatGPT**
   - Add both connectors
   - Test widget functionality

---

## Reference Commands

```bash
# Check Railway project status
railway status

# Watch deployment logs
railway logs --follow

# Set environment variable
railway variables --set "KEY=VALUE"

# Get project domain
railway domain

# Trigger new deployment
railway up

# Check service logs
railway logs

# View project info
railway whoami
```

---

## Additional Resources

- Railway Documentation: https://docs.railway.app/
- Nixpacks Documentation: https://nixpacks.com/
- Project Dashboard: https://railway.com/project/515017a7-caac-4cc8-af45-0811b5fe4d27
- GitHub Repository: https://github.com/spencergrantkyle/appsdk_draftworx
- Build Logs: https://railway.com/project/515017a7-caac-4cc8-af45-0811b5fe4d27/service/f793b66f-7af5-42cf-93da-cacbfe1ec432

---

*Last Updated: After initial Railway deployment attempt*

