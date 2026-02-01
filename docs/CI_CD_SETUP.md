# CI/CD for RapidAPI OpenAPI Specs

This GitHub Actions workflow automatically generates OpenAPI specifications from your FastAPI app and updates them on RapidAPI whenever you push changes.

## 🔄 What It Does

When you push changes to `main.py` or any file in `ecomarine/`:

1. ✅ Starts FastAPI server locally
2. ✅ Extracts OpenAPI JSON from `/openapi.json` endpoint
3. ✅ Converts to YAML format
4. ✅ Updates specs on RapidAPI via API
5. ✅ Commits updated specs back to repo

## 🔐 Required Secrets

You need to add these 3 secrets to your GitHub repository:

| Secret Name | Value | Where to Find |
|-------------|-------|---------------|
| `RAPIDAPI_KEY` | Your RapidAPI provider key | [RapidAPI Dashboard](https://rapidapi.com/developer/dashboard) → Authorization |
| `RAPIDAPI_API_ID` | `api_7bd483b9-3862-4fab-97b7-7c1e0f58e408` | Already provided |
| `RAPIDAPI_VERSION_ID` | `apiversion_2ba128c1-0903-43a6-84d4-f81d1477164c` | Already provided |

## 🚀 Quick Setup

### Option 1: Automated Setup Script

```bash
# Run the setup script
./scripts/setup-rapidapi-secrets.sh
```

This will prompt you for your RapidAPI key and automatically configure all secrets.

### Option 2: Manual Setup via GitHub UI

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** for each secret:
   - `RAPIDAPI_KEY` - your RapidAPI provider key
   - `RAPIDAPI_API_ID` - `api_7bd483b9-3862-4fab-97b7-7c1e0f58e408`
   - `RAPIDAPI_VERSION_ID` - `apiversion_2ba128c1-0903-43a6-84d4-f81d1477164c`

### Option 3: Using GitHub CLI

```bash
# Set RAPIDAPI_KEY
gh secret set RAPIDAPI_KEY --body "your_rapidapi_key_here"

# Set RAPIDAPI_API_ID
gh secret set RAPIDAPI_API_ID --body "api_7bd483b9-3862-4fab-97b7-7c1e0f58e408"

# Set RAPIDAPI_VERSION_ID
gh secret set RAPIDAPI_VERSION_ID --body "apiversion_2ba128c1-0903-43a6-84d4-f81d1477164c"
```

## 📋 Workflow Triggers

The workflow runs on:
- ✅ Push to `main` branch that modifies `main.py` or `ecomarine/**/*.py`
- ✅ Manual trigger from GitHub Actions tab (workflow_dispatch)
- ✅ Changes to the workflow file itself

## 🧪 Testing the Workflow

### Test 1: Manual Trigger

1. Go to **Actions** tab in your GitHub repo
2. Click **"Update RapidAPI OpenAPI Specs"** workflow
3. Click **"Run workflow"** → **"Run workflow"**
4. Watch the logs for success/failure

### Test 2: Automatic Trigger

1. Make a small change to `main.py` (e.g., update a docstring)
2. Commit and push to main
3. Go to **Actions** tab to see the workflow run
4. Check if OpenAPI specs are updated on RapidAPI

## 🔍 Troubleshooting

### Issue: "RapidAPI update returned HTTP 401"

**Solution:** Your `RAPIDAPI_KEY` is incorrect. Make sure you're using the **Provider Key** (not the consumer key). Get it from your RapidAPI Developer Dashboard.

### Issue: "RapidAPI update returned HTTP 404"

**Solution:** The API ID or Version ID is incorrect. Double-check the values:
- API ID: `api_7bd483b9-3862-4fab-97b7-7c1e0f58e408`
- Version ID: `apiversion_2ba128c1-0903-43a6-84d4-f81d1477164c`

### Issue: "Failed to generate OpenAPI JSON"

**Solution:** The FastAPI server failed to start. Check:
- Dependencies are installed (`uv sync` works locally?)
- Port 8000 is available
- No syntax errors in `main.py`

### Issue: Workflow not triggering

**Solution:** 
- Make sure you're pushing to `main` branch
- Changes must be in `main.py` or `ecomarine/` directory
- Or manually trigger from Actions tab

## 📁 Files Generated

The workflow generates/updates:
- `openapi.json` - OpenAPI spec in JSON format
- `openapi.yaml` - OpenAPI spec in YAML format

Both are committed back to the repository for version control.

## 🎯 Benefits

✅ **No manual work** - Specs auto-update when code changes  
✅ **Always in sync** - RapidAPI reflects latest API changes  
✅ **Version control** - Specs tracked in git  
✅ **Fast iteration** - Deploy API changes in minutes  
✅ **Documentation** - Auto-generated from code comments  

## 📞 Support

If you encounter issues:
1. Check the **Actions** tab logs for detailed error messages
2. Verify all secrets are set correctly
3. Test locally: `python -c "import main; print('OK')"`
4. Contact: deepeshkalurs@gmail.com

---

**Last Updated:** 2026-02-01
