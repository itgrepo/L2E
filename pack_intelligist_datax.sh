#!/bin/bash

# =================================================================
# Intelligist DataX - Release Packager
# =================================================================

PROJECT_NAME="Intelligist_DataX_Platform"
VERSION="3.4.1"
OUTPUT_ZIP="${PROJECT_NAME}_Installer_v${VERSION}.zip"
RELEASE_DIR="release_intelligist_datax"

echo "📦 Starting Intelligist DataX Packaging v${VERSION}..."

# 1. Clean up previous release
rm -rf $RELEASE_DIR
rm -f $OUTPUT_ZIP
mkdir -p $RELEASE_DIR

# 2. Build Docker Images
echo "🏗️  Building Docker Images (Linux/amd64 format)..."
export DOCKER_DEFAULT_PLATFORM=linux/amd64
docker-compose -f docker-compose.uat.yml build

echo "🏷️  Tagging images..."
docker tag intelligist_datax_backend:latest intelligist-datax-backend:prod 2>/dev/null || docker tag intelligistdatax_backend:latest intelligist-datax-backend:prod 2>/dev/null || true
docker tag intelligist_datax_frontend:latest intelligist-datax-frontend:prod 2>/dev/null || docker tag intelligistdatax_frontend:latest intelligist-datax-frontend:prod 2>/dev/null || true

# Fallback tagging just in case directory name is different
BACKEND_IMG=$(docker images | grep backend | grep -v prod | awk 'NR==1{print $1":"$2}')
FRONTEND_IMG=$(docker images | grep frontend | grep -v prod | awk 'NR==1{print $1":"$2}')
if [ ! -z "$BACKEND_IMG" ]; then docker tag $BACKEND_IMG intelligist-datax-backend:prod 2>/dev/null; fi
if [ ! -z "$FRONTEND_IMG" ]; then docker tag $FRONTEND_IMG intelligist-datax-frontend:prod 2>/dev/null; fi

echo "💾 Exporting Docker Images..."
if docker info > /dev/null 2>&1; then
    docker save intelligist-datax-backend:prod > $RELEASE_DIR/backend.tar
    docker save intelligist-datax-frontend:prod > $RELEASE_DIR/frontend.tar
    echo "✅ Docker images exported successfully."
else
    echo "❌ Docker not running. Failed to export images."
    echo "⚠️ WARNING: The installer will be incomplete!"
fi

# 3. Copy Installer Files
echo "📂 Copying installer files..."
cp setup.sh $RELEASE_DIR/
cp setup_ui.py $RELEASE_DIR/
cp init_db_uat.sh $RELEASE_DIR/
cp Installation_Manual.md $RELEASE_DIR/
cp docker-compose.prod.yml $RELEASE_DIR/
cp .env.example $RELEASE_DIR/
cp intelligist_datax_full_dump.sql $RELEASE_DIR/

# Copy SSL & Nginx configs
mkdir -p $RELEASE_DIR/frontend
cp frontend/nginx.conf $RELEASE_DIR/frontend/
cp frontend/nginx.ssl.conf $RELEASE_DIR/frontend/
cp -r demo_ssl $RELEASE_DIR/

# 4. Zip it up
echo "🤐 Creating zip package: $OUTPUT_ZIP..."
zip -r $OUTPUT_ZIP $RELEASE_DIR

echo "==============================================================="
echo "✅ Packaging Complete!"
echo "📦 File: $OUTPUT_ZIP"
echo "==============================================================="
