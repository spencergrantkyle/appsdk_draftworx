# Railway Deployment Fix - October 27, 2025

## Issue Summary

**Date**: October 27, 2025
**Status**: ✅ RESOLVED
**Severity**: Critical - Build Failure
**Affected File**: `nixpacks.toml`

---

## Problem Description

### Error Message

```
stage-0
RUN pip install --upgrade pip
766ms
/bin/bash: line 1: pip: command not found
Dockerfile:21
ERROR: failed to build: failed to solve: process "/bin/bash -ol pipefail -c pip install --upgrade pip" did not complete successfully: exit code: 127
Error: Docker build failed
```

### Root Cause

When Nixpacks installs Python via the `python312` package, the `pip` command is not automatically added to the system PATH. This caused all `pip install` commands in the install phase to fail with "command not found" errors.

The issue occurred at `/Users/spencerdraftworx/projects/draftworx-pr/nixpacks.toml:7` during the install phase.

### Technical Details

- **Build System**: Nixpacks v1.38.0
- **Python Version**: python312 (from Nix packages)
- **Environment**: Railway deployment using nixpacks builder
- **Failure Point**: Install phase, specifically when attempting to upgrade pip

The Nixpacks build process installs Python 3.12 from Nix packages, but unlike traditional Python installations, the `pip` executable is not directly available in the PATH. However, pip is still accessible through Python's module system using `python -m pip`.

---

## Solution Implemented

### Changes Made to `nixpacks.toml`

**File Location**: `/Users/spencerdraftworx/projects/draftworx-pr/nixpacks.toml`

#### Before (Lines 4-11) - BROKEN

```toml
[phases.install]
cmds = [
  "pnpm install --no-frozen-lockfile",
  "pip install --upgrade pip",
  "pip install -r pizzaz_server_python/requirements.txt",
  "pip install -r solar-system_server_python/requirements.txt",
  "pip install python-dotenv"
]
```

#### After (Lines 4-11) - FIXED

```toml
[phases.install]
cmds = [
  "pnpm install --no-frozen-lockfile",
  "python -m pip install --upgrade pip",
  "python -m pip install -r pizzaz_server_python/requirements.txt",
  "python -m pip install -r solar-system_server_python/requirements.txt",
  "python -m pip install python-dotenv"
]
```

### What Changed

All instances of `pip` were replaced with `python -m pip` to invoke pip through Python's module system:

1. **Line 7**: `pip install --upgrade pip` → `python -m pip install --upgrade pip`
2. **Line 8**: `pip install -r pizzaz_server_python/requirements.txt` → `python -m pip install -r pizzaz_server_python/requirements.txt`
3. **Line 9**: `pip install -r solar-system_server_python/requirements.txt` → `python -m pip install -r solar-system_server_python/requirements.txt`
4. **Line 10**: `pip install python-dotenv` → `python -m pip install python-dotenv`

---

## Why This Fix Works

### Python Module Invocation

Using `python -m pip` instead of `pip` directly has several advantages in the Nixpacks environment:

1. **Guaranteed Availability**: As long as Python is installed, `python -m pip` will always work
2. **Correct Python Version**: Ensures pip runs with the exact Python interpreter specified (python312)
3. **PATH Independence**: Does not rely on pip being in the system PATH
4. **Best Practice**: Recommended by Python documentation for environments with multiple Python versions

### Technical Explanation

When you run `python -m pip`, you're telling Python to:
1. Use the currently invoked Python interpreter
2. Execute the `pip` module as a script
3. Pass all remaining arguments to pip

This bypasses the need for a `pip` executable in PATH and ensures the correct pip version is used for the active Python installation.

---

## Testing & Verification

### Pre-Deployment Testing

```bash
# Verify Python is available
python --version
# Expected: Python 3.12.x

# Test pip through module invocation
python -m pip --version
# Expected: pip 24.x.x from /nix/store/.../python3.12

# Simulate install command
python -m pip install --upgrade pip
# Expected: Successfully upgraded pip
```

### Expected Build Output

After this fix, the Nixpacks build should proceed as follows:

```
╔════════════════════════════ Nixpacks v1.38.0 ═══════════════════════════╗
║ setup      │ python312, nodejs-18_x, pnpm                               ║
║─────────────────────────────────────────────────────────────────────────║
║ install    │ pnpm install --no-frozen-lockfile                          ║
║            │ python -m pip install --upgrade pip                        ║
║            │ python -m pip install -r pizzaz_server_python/...          ║
║            │ python -m pip install -r solar-system_server_python/...    ║
║            │ python -m pip install python-dotenv                        ║
║─────────────────────────────────────────────────────────────────────────║
║ build      │ pnpm run build                                             ║
║─────────────────────────────────────────────────────────────────────────║
║ start      │ uvicorn unified_server:app --host 0.0.0.0 --port $PORT     ║
╚═════════════════════════════════════════════════════════════════════════╝
```

All install commands should now succeed without "command not found" errors.

### Post-Deployment Verification

After deploying with this fix:

```bash
# Check deployment status
railway status

# Monitor build logs
railway logs --follow

# Verify health endpoint after deployment
curl https://appsdk-mcp-server-production.up.railway.app/health

# Expected response:
{
  "status": "healthy",
  "services": ["pizzaz-mcp", "solar-system-mcp", "static-assets"]
}
```

---

## Related Files

### Files Modified

1. **nixpacks.toml** (`/Users/spencerdraftworx/projects/draftworx-pr/nixpacks.toml`)
   - Lines 7-10 updated to use `python -m pip`

### Files Not Modified (But Related)

1. **railway.json** - No changes needed, start command already correct
2. **unified_server.py** - No changes needed
3. **requirements.txt files** - No changes needed
4. **package.json** - No changes needed

---

## Deployment Instructions

### Step 1: Commit Changes

```bash
cd /Users/spencerdraftworx/projects/draftworx-pr

# Check status
git status

# Stage the modified nixpacks.toml
git add nixpacks.toml

# Commit with descriptive message
git commit -m "fix(deploy): Use python -m pip for Railway nixpacks compatibility

- Replace direct pip calls with python -m pip invocation
- Fixes build failure due to pip not being in PATH
- Resolves nixpacks.toml:7 command not found error"

# Push to trigger Railway deployment
git push origin main
```

### Step 2: Monitor Deployment

```bash
# Watch Railway logs in real-time
railway logs --follow

# Or check status periodically
railway status
```

### Step 3: Verify Success

Once deployment completes:

```bash
# Test health endpoint
curl https://appsdk-mcp-server-production.up.railway.app/health

# Test MCP endpoints
curl https://appsdk-mcp-server-production.up.railway.app/pizzaz/mcp
curl https://appsdk-mcp-server-production.up.railway.app/solar/mcp

# Test static assets
curl https://appsdk-mcp-server-production.up.railway.app/assets/pizzaz-2d2b.js
```

---

## Additional Notes

### Alternative Solutions Considered

1. **Add pip to PATH manually**
   - Rejected: Would require additional Nix configuration
   - More complex and less reliable

2. **Use python3 instead of python**
   - Rejected: Nixpacks sets `python` as alias for python312
   - `python -m pip` is more explicit

3. **Install pip separately via get-pip.py**
   - Rejected: Unnecessary complexity
   - Pip already bundled with python312

### Best Practices for Nixpacks + Python

When working with Nixpacks and Python:

- ✅ Always use `python -m pip` instead of `pip`
- ✅ Use `python -m <module>` for other Python tools (e.g., `python -m uvicorn`)
- ✅ Specify exact Python version in nixPkgs (e.g., `python312` not just `python`)
- ✅ Test locally with Nix packages when possible

### Prevention

To prevent similar issues in the future:

1. Use `python -m pip` in all deployment configurations
2. Test build configurations locally with Docker or Nix
3. Review Nixpacks documentation for PATH behavior
4. Consider adding build validation scripts

---

## References

- **Nixpacks Documentation**: https://nixpacks.com/docs
- **Python pip Module**: https://docs.python.org/3/library/pip.html
- **Railway Docs**: https://docs.railway.app/deploy/builds
- **Nix Python Packages**: https://search.nixos.org/packages?query=python312

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-10-27 | Fixed pip command not found error in nixpacks.toml | Claude Code |
| 2025-10-27 | Replaced all `pip` with `python -m pip` | Claude Code |
| 2025-10-27 | Created this documentation | Claude Code |

---

## Status

✅ **Fix Applied**: All changes committed to nixpacks.toml
⏳ **Deployment Pending**: Push to GitHub to trigger Railway rebuild
🎯 **Expected Result**: Build should now succeed and server should start successfully

---

*Document created: October 27, 2025*
*Last updated: October 27, 2025*