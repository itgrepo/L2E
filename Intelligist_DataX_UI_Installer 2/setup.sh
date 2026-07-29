#!/bin/bash

# =================================================================
# Intelligist DataX - UI Installation Launcher (AIS Cloud Edition)
# =================================================================

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "==============================================================="
echo "   🚀 เริ่มต้นเข้าสู่โหมดติดตั้งผ่าน Web UI"
echo "==============================================================="
echo -e "${NC}"

# 1. Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: ไม่พบ Python 3 ในระบบ${NC}"
    echo "กรุณาติดตั้ง Python 3 ก่อนรันคำสั่งนี้ (เช่น sudo apt install python3)"
    exit 1
fi

# 2. Check for docker and docker-compose
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: ไม่พบ Docker หรือ Docker Compose ในระบบ${NC}"
    echo "กรุณาติดตั้ง Docker ให้เรียบร้อยก่อน"
    exit 1
fi

# 3. Retrieve machine IP and Output Links
IP=$(hostname -I | awk '{print $1}')
if [ -z "$IP" ]; then
    IP="localhost"
fi

echo -e "${CYAN}กำลังจำลอง Web Server สำหรับหน้าจอติดตั้ง...${NC}"
echo -e "กรุณาเปิดเว็บบราวเซอร์ของคุณ (Chrome/Edge/Firefox) แล้วไปที่ URL ด้านล่างนี้:\n"
echo -e "${YELLOW}  👉  http://$IP:8080 ${NC}"
echo -e "\n(หากเข้าไม่ได้ ให้ลองใช้ http://localhost:8080 แทน หรือตรวจสอบ Firewall ว่าเปิด Port 8080 หรือยัง)\n"
echo -e "กด Ctrl+C หากต้องการยกเลิกการติดตั้ง"
echo -e "---------------------------------------------------------------\n"

# 4. Launch the Python web server
python3 setup_ui.py
