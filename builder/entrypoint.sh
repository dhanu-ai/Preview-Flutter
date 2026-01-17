#!/bin/bash
set -e

PROJECT_NAME=${PROJECT_NAME:-fitnesstracker}
PROJECT_ID=${PROJECT_ID:-_mXaP2CpM_XDOu8UhbrIk}
PROJECT_DIR=/app/$PROJECT_NAME
UI_DIR=/ui

echo "🚀 Building project: $PROJECT_NAME ($PROJECT_ID)"

# Create Flutter project
flutter create $PROJECT_NAME
cd $PROJECT_DIR

# Fetch project JSON from Supabase
echo "📥 Fetching project from Supabase"
python3 << EOF
import os
import json
import requests

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
PROJECT_ID = os.environ.get("PROJECT_ID")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise Exception("Supabase env vars not set")

headers = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
}
response = requests.get(f"{SUPABASE_URL}/rest/v1/projects?id=eq.{PROJECT_ID}", headers=headers)
response.raise_for_status()
data = response.json()
if not data:
    raise Exception(f"No project found for ID {PROJECT_ID}")

project_json = data[0]["project_json"]

root = "/app/$PROJECT_NAME"
for path, content in project_json["files"].items():
    full_path = os.path.join(root, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("✅ Project files written")
EOF

# Install Flutter dependencies
echo "📦 Running flutter pub get"
flutter pub get

# Build Flutter web
echo "🌐 Building Flutter Web"
flutter build web

# Copy to shared UI folder
echo "📤 Copying build to /ui"
mkdir -p $UI_DIR
cp -r build/web/* $UI_DIR

echo "✅ Flutter Web build completed"
