@echo off
chcp 65001 >nul
echo ===============================================================
echo    🚀 เริ่มต้นเข้าสู่โหมดติดตั้งผ่าน Web UI (Windows)
echo ===============================================================

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] ไม่พบ Python ในระบบ
    echo กรุณาติดตั้ง Python (จาก Microsoft Store หรือ python.org) ก่อนเริ่มการทำงาน
    pause
    exit /b 1
)

:: Check for Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] ไม่พบ Docker ในระบบ
    echo กรุณาติดตั้ง Docker Desktop ก่อนเริ่มการทำงาน
    pause
    exit /b 1
)

echo กำลังจำลอง Web Server สำหรับหน้าจอติดตั้ง...
echo กรุณาเปิดเว็บบราวเซอร์ของคุณ (Chrome/Edge/Firefox) แล้วไปที่ URL:
echo   👉  http://localhost:8080
echo.
echo กด Ctrl+C หากต้องการยกเลิกการติดตั้ง
echo ---------------------------------------------------------------

:: Run Python script
python setup_ui.py

pause
