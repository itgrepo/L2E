#!/bin/bash

# =================================================================
# Intelligist DataX - Offline Package Builder (Source Code Protection)
# =================================================================

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "==============================================================="
echo "   📦 เริ่มขั้นตอนการแพ็กเกจระบบแบบ Offline (ไร้ Source Code)"
echo "==============================================================="
echo -e "${NC}"

# Set platform to force building for Linux x86 Server (Avoiding Mac M1/M2 ARM64 crash)
export DOCKER_DEFAULT_PLATFORM=linux/amd64

# 1. Build Docker Images
echo -e "${YELLOW}[1/4] กำลัง Build อิมเมจ Docker (Backend & Frontend)...${NC}"
# Use the UAT compose file which contains the build configurations
docker-compose -f docker-compose.uat.yml build


# Tag the built images cleanly
echo "Tagging images..."
docker tag l2e-backend_backend:latest l2e-backend:prod 2>/dev/null || docker tag astro_backend_uat_backend:latest l2e-backend:prod 2>/dev/null || docker tag project_l2e-backend:latest l2e-backend:prod 2>/dev/null || true
docker tag l2e-frontend_frontend:latest l2e-frontend:prod 2>/dev/null || docker tag astro_frontend_uat_frontend:latest l2e-frontend:prod 2>/dev/null || docker tag project_l2e-frontend:latest l2e-frontend:prod 2>/dev/null || true

# Try to find exactly what compose built
BACKEND_IMG=$(docker images | grep backend | grep -v prod | awk 'NR==1{print $1":"$2}')
FRONTEND_IMG=$(docker images | grep frontend | grep -v prod | awk 'NR==1{print $1":"$2}')

if [ ! -z "$BACKEND_IMG" ]; then docker tag $BACKEND_IMG l2e-backend:prod; fi
if [ ! -z "$FRONTEND_IMG" ]; then docker tag $FRONTEND_IMG l2e-frontend:prod; fi


# 2. Setup Release Directory
echo -e "${YELLOW}[2/4] กำลังเตรียมโฟลเดอร์สำหรับส่งให้ลูกค้า (release/)...${NC}"
rm -rf release/
mkdir -p release/backendold/Astro_backend

# 3. Export Docker Images
echo -e "${YELLOW}[3/4] กำลังแพ็กก้อน Image (.tar) เพื่อให้ลูกค้านำไปติดตั้งแบบ Offline...${NC}"
echo "(ขั้นตอนนี้อาจใช้เวลานาน โปรดรอสักครู่)"
docker save -o release/backend.tar l2e-backend:prod
docker save -o release/frontend.tar l2e-frontend:prod

# 4. Copy Installation Files & DB Scripts
echo -e "${YELLOW}[4/4] กำลังคัดลอกไฟล์ตั้งค่า...${NC}"
cp setup.sh release/
cp setup_ui.py release/
cp docker-compose.prod.yml release/docker-compose.prod.yml
cp .env.example release/.env.example
cp init_db_uat.sh release/
cp Installation_Manual.md release/

# Copy only the SQL scripts (no python/source code) for DB initialization
cp backendold/Astro_backend/*.sql release/backendold/Astro_backend/

echo -e "${GREEN}"
echo "==============================================================="
echo "   ✅ แพ็กเกจเสร็จสมบูรณ์!"
echo "==============================================================="
echo -e "${NC}"
echo "วิธีใช้งาน:"
echo "1. เข้าไปที่โฟลเดอร์ release:  cd release/"
echo "2. หรือบีบอัดเป็น .zip เพื่อส่งให้ลูกค้า: zip -r DEX_L2E_Installer.zip release/"
echo "(ลูกค้าจะได้ไปแค่ไฟล์ .tar, .yml, .sh และ UI setup เท่านั้น โดยไม่มี Source Code ของโปรแกรมเลย)"
