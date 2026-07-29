#!/bin/bash

# Define version and date code
VERSION="3.4.2"
DATE_CODE=$(date +"%Y%m%d_%H%M")
ZIP_NAME="Intelligist_DataX_Installer_v${VERSION}_${DATE_CODE}.zip"
INSTALLER_DIR="Intelligist_DataX_UI_Installer"

echo "============================================================"
echo "📦 Building Daily Installer: $ZIP_NAME"
echo "============================================================"

# Clean up previous installer directories
rm -rf ${INSTALLER_DIR}
mkdir -p ${INSTALLER_DIR}

# Copy core source code and configurations
echo "Copying Backend..."
cp -r backendold ${INSTALLER_DIR}/
echo "Copying Frontend..."
cp -r frontend ${INSTALLER_DIR}/
echo "Copying Demo SSL..."
cp -r demo_ssl ${INSTALLER_DIR}/

# Copy Setup Scripts and Configs
echo "Copying Configuration and Scripts..."
cp docker-compose.3001.yml ${INSTALLER_DIR}/docker-compose.yml
cp init_db_uat.sh ${INSTALLER_DIR}/
cp setup ${INSTALLER_DIR}/
cp setup.sh ${INSTALLER_DIR}/
cp setup.bat ${INSTALLER_DIR}/
cp setup_ui.py ${INSTALLER_DIR}/
cp intelligist_datax_full_dump.sql ${INSTALLER_DIR}/
cp .env.example ${INSTALLER_DIR}/
cp README_INSTALL.txt ${INSTALLER_DIR}/

# SSL configuration and frontend ports are now defined statically in docker-compose.3001.yml

# Clean up bulky/compiled folders to keep zip small
echo "Cleaning up temp/compiled files..."
rm -rf ${INSTALLER_DIR}/backendold/Astro_backend/venv
rm -rf ${INSTALLER_DIR}/backendold/Astro_backend/__pycache__
rm -rf ${INSTALLER_DIR}/frontend/node_modules
rm -rf ${INSTALLER_DIR}/frontend/dist

# Zip the package
echo "Zipping the package..."
rm -f Intelligist_DataX_Installer_v*.zip
zip -q -r ${ZIP_NAME} ${INSTALLER_DIR}/

echo "============================================================"
echo "✅ Package Built Successfully!"
echo "📍 File: ${ZIP_NAME}"
ls -lh ${ZIP_NAME}
echo "============================================================"
