#!/bin/bash
# Generate OpenAPI specs from FastAPI app for pre-commit hook
# This runs locally before commits

set -e

echo "📄 Generating OpenAPI specifications..."

# Check if server is already running
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Using existing FastAPI server on port 8000"
else
    echo "🚀 Starting FastAPI server temporarily..."
    uv run uvicorn main:app --host 0.0.0.0 --port 8000 &
    SERVER_PID=$!
    
    # Wait for server
    for i in {1..30}; do
        if curl -s http://localhost:8000/ > /dev/null 2>&1; then
            echo "✅ Server ready"
            break
        fi
        echo "⏳ Waiting for server... ($i/30)"
        sleep 1
    done
fi

# Generate OpenAPI JSON
echo "📥 Downloading OpenAPI JSON..."
if curl -s http://localhost:8000/openapi.json > openapi.json.tmp; then
    if [ -s openapi.json.tmp ]; then
        mv openapi.json.tmp openapi.json
        echo "✅ openapi.json generated ($(wc -c < openapi.json) bytes)"
    else
        echo "❌ Failed: Empty response"
        rm -f openapi.json.tmp
        exit 1
    fi
else
    echo "❌ Failed to download OpenAPI specs"
    rm -f openapi.json.tmp
    exit 1
fi

# Convert to YAML
echo "📄 Converting to YAML..."
uv run python -c "
import json
import yaml
with open('openapi.json', 'r') as f:
    data = json.load(f)
with open('openapi.yaml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
print('✅ openapi.yaml generated')
"

# Cleanup - kill server if we started it
if [ -n "$SERVER_PID" ]; then
    echo "🧹 Stopping temporary server..."
    kill $SERVER_PID 2>/dev/null || true
    sleep 1
fi

echo "✨ OpenAPI specs generated successfully!"
echo "   - openapi.json"
echo "   - openapi.yaml"
echo "   - .rapidapi/tests/* (from test extraction)"

# Stage the generated files for commit
git add openapi.json openapi.yaml .rapidapi/tests/ 2>/dev/null || true

echo "📦 Files staged for commit"
