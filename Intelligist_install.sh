#!/bin/bash
set -Eeuo pipefail

# สีสันสำหรับการแสดงผล
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}======================================================${NC}"
echo -e "${GREEN}   🚀 Intelligist DataX - Installer                   ${NC}"
echo -e "${GREEN}======================================================${NC}"

# 1. ตรวจสอบว่ามี Docker และ Docker Compose ไหม
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ ไม่พบ Docker หรือ Docker Compose ในเครื่องนี้${NC}"
    echo -e "กรุณาติดตั้ง Docker ก่อนเริ่มรันตัวติดตั้ง"
    exit 1
fi

echo -e "\n${YELLOW}[1/3] กำลังสร้างและเริ่มการทำงานของ Container (Backend, Frontend, Database)...${NC}"
docker-compose up -d --build

echo -e "\n${YELLOW}[2/3] รอให้ Database พร้อมทำงาน (อาจใช้เวลาประมาณ 10-20 วินาที)...${NC}"
MAX_TRIES=20
COUNT=0
while ! docker exec datax_db_3001 mysqladmin ping -uastro -p"${DB_PASS:-}" --silent; do
    echo "กำลังรอ Database... ($((++COUNT))/$MAX_TRIES)"
    sleep 2
    if [ $COUNT -ge $MAX_TRIES ]; then
        echo -e "${RED}❌ Error: Database ไม่พร้อมทำงานในเวลาที่กำหนด${NC}"
        exit 1
    fi
done

echo -e "\n${YELLOW}[3/3] กำลังนำเข้าข้อมูล (Import Database Dump)...${NC}"
if [ -f intelligist_datax_full_dump.sql ]; then
    docker exec -i datax_db_3001 mysql -uastro -p"${DB_PASS:-}" datax_db_3001 < intelligist_datax_full_dump.sql
    echo -e "${GREEN}✅ นำเข้าข้อมูลสำเร็จ!${NC}"
else
    echo -e "${RED}❌ Error: ไม่พบไฟล์ intelligist_datax_full_dump.sql${NC}"
    exit 1
fi

echo -e "\n${GREEN}======================================================${NC}"
echo -e "${GREEN}   🎉 ติดตั้งเสร็จสมบูรณ์!                            ${NC}"
echo -e "${GREEN}======================================================${NC}"
echo -e "ระบบพร้อมใช้งานแล้วที่:"
IP=$(hostname -I | awk '{print $1}')
echo -e "👉 http://${IP:-localhost}:3001"
echo ""
