import http.server
import socketserver
import json
import os
import subprocess
import threading
import urllib.parse
from http import HTTPStatus

PORT = 8080
LOG_FILE = "setup_install.log"
ENV_TEMPLATE_FILE = ".env.example"
ENV_FILE = ".env"

# Ensure log file exists and is empty
open(LOG_FILE, 'w').close()

UI_HTML = """<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Intelligist DataX - Setup Wizard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f3f4f6; }
        .glass-panel { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); }
        .terminal { background-color: #1e1e1e; color: #00ff00; font-family: monospace; }
        .spinner {
            border: 4px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top: 4px solid #3b82f6;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body class="flex items-center justify-center min-h-screen p-4">

    <div class="glass-panel w-full max-w-4xl rounded-2xl shadow-2xl overflow-hidden flex flex-col md:flex-row min-h-[600px] transition-all duration-500">
        
        <!-- Left Sidebar / Info -->
        <div class="bg-blue-600 text-white p-8 md:w-1/3 flex flex-col justify-between">
            <div>
                <img src="https://upload.wikimedia.org/wikipedia/commons/e/e4/AIS_logo_2016.svg" alt="AIS Cloud" class="h-10 mb-8 filter brightness-0 invert opacity-80">
                <h1 class="text-3xl font-bold mb-2">Intelligist DataX Setup</h1>
                <p class="text-blue-200 text-sm opacity-90">เครื่องมือช่วยติดตั้งแบบอัตโนมัติ สำหรับ Intelligist DataX บน AIS Cloud</p>
                
                <div class="mt-6 bg-blue-700/50 p-4 rounded-xl border border-blue-500/30">
                    <div class="flex items-center gap-2 mb-2">
                        <span class="bg-blue-500 text-white text-xs font-bold px-2 py-1 rounded">v3.4.1 (Dynamic Page Builder)</span>
                        <span class="text-blue-200 text-xs text-opacity-80">อัปเดตล่าสุด</span>
                    </div>
                    <ul class="text-xs text-blue-100 space-y-1 mt-2 list-disc pl-4 opacity-90">
                        <li>เพิ่มระบบ <strong>Dynamic Page Builder</strong> ปรับแก้ข้อความหน้าแรกได้ดั่งใจ</li>
                        <li>รองรับการสลับตำแหน่ง, ซ่อน/แสดง Component แบบ Real-time</li>
                        <li>ระบบ Admin UI คล้าย Elementor ไม่ต้องแก้ไข Source Code</li>
                        <li>ปรับปรุงระบบนำทาง (Mobile Fixed Navbar) และแถบ Sticky Side Tab</li>
                        <li>เพิ่มระบบ Dashboard Stats & Activity Monitoring แบบเรียลไทม์</li>
                    </ul>
                </div>
                
                <ul class="mt-8 space-y-4">
                    <li class="flex items-center space-x-3 text-sm" id="step-1-marker">
                        <span class="flex-shrink-0 w-6 h-6 rounded-full bg-white text-blue-600 flex items-center justify-center font-bold">1</span>
                        <span>ระบุข้อมูลเครือข่าย</span>
                    </li>
                    <li class="flex items-center space-x-3 text-sm opacity-50 transition-opacity" id="step-2-marker">
                        <span class="flex-shrink-0 w-6 h-6 rounded-full border-2 border-white flex items-center justify-center font-bold">2</span>
                        <span>ตั้งค่าระบบฐานข้อมูล</span>
                    </li>
                    <li class="flex items-center space-x-3 text-sm opacity-50 transition-opacity" id="step-3-marker">
                        <span class="flex-shrink-0 w-6 h-6 rounded-full border-2 border-white flex items-center justify-center font-bold">3</span>
                        <span>รอการติดตั้งและรันระบบ</span>
                    </li>
                </ul>
            </div>
            
            <div class="mt-8 text-xs text-blue-200">
                &copy; 2026 Intelligist
            </div>
        </div>

        <!-- Right Content Area -->
        <div class="p-8 md:w-2/3 flex flex-col bg-white">
            
            <!-- Setup Form -->
            <form id="setupForm" class="flex-1 flex flex-col transition-all duration-300">
                
                <!-- Step 1: Network -->
                <div id="step-1" class="flex-1 block">
                    <h2 class="text-2xl font-semibold mb-6 text-gray-800 border-b pb-2">🌐 ตั้งค่าเครือข่ายพื้นฐาน</h2>
                    
                    <div class="space-y-5">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">เซิร์ฟเวอร์ IP / โดเมน <span class="text-red-500">*</span></label>
                            <input type="text" id="SERVER_IP" name="SERVER_IP" placeholder="เช่น 192.168.1.100 หรือ intelligist-datax.ais.co.th" required
                                class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow">
                            <p class="text-xs text-gray-500 mt-1">IP ของเครื่องนี้ เพื่อให้ภายนอกเข้าถึงระบบได้</p>
                        </div>
                        
                        <div class="flex space-x-4">
                            <div class="w-1/2">
                                <label class="block text-sm font-medium text-gray-700 mb-1">พอร์ตสำหรับ Frontend</label>
                                <input type="number" id="FRONTEND_PORT" name="FRONTEND_PORT" value="3001" required
                                    class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500">
                            </div>
                            <div class="w-1/2">
                                <label class="block text-sm font-medium text-gray-700 mb-1">พอร์ตสำหรับ Backend</label>
                                <input type="number" id="BACKEND_PORT" name="BACKEND_PORT" value="3010" required
                                    class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500">
                            </div>
                        </div>

                        <!-- SSL / HTTPS Configuration -->
                        <div class="bg-indigo-50 p-4 rounded-xl border border-indigo-100 space-y-4">
                            <div class="flex items-center justify-between">
                                <h3 class="text-sm font-semibold text-indigo-900 flex items-center gap-2">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                                    การตั้งค่าความปลอดภัย (SSL / HTTPS)
                                </h3>
                                <label class="relative inline-flex items-center cursor-pointer">
                                    <input type="checkbox" name="ENABLE_SSL" id="ENABLE_SSL" class="sr-only peer" onchange="toggleSSLFields()">
                                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                                </label>
                            </div>
                            
                            <div id="ssl-fields" class="hidden space-y-3 pt-2 border-t border-indigo-100">
                                <div>
                                    <label class="block text-xs font-medium text-indigo-700 mb-1">พาธของ SSL Certificate (.crt / .pem) <span class="text-red-500">*</span></label>
                                    <input type="text" id="SSL_CERT_PATH" name="SSL_CERT_PATH" placeholder="เช่น /etc/nginx/ssl/server.crt"
                                        class="w-full px-3 py-2 text-sm rounded-md border border-gray-300 focus:ring-1 focus:ring-indigo-500">
                                </div>
                                <div>
                                    <label class="block text-xs font-medium text-indigo-700 mb-1">พาธของ SSL Private Key (.key) <span class="text-red-500">*</span></label>
                                    <input type="text" id="SSL_KEY_PATH" name="SSL_KEY_PATH" placeholder="เช่น /etc/nginx/ssl/server.key"
                                        class="w-full px-3 py-2 text-sm rounded-md border border-gray-300 focus:ring-1 focus:ring-indigo-500">
                                </div>
                                <p class="text-[10px] text-indigo-500 italic">* ระบบจะทำการ Mount ไฟล์จาก Path ที่ระบุ เข้าไปยัง Container อัตโนมัติ</p>
                            </div>
                        </div>
                    </div>

                    <div class="mt-8 flex justify-end">
                        <button type="button" onclick="nextStep(2)" class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg shadow-md transition-colors flex items-center">
                            ถัดไป <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                        </button>
                    </div>
                </div>

                <!-- Step 2: Database & SMTP -->
                <div id="step-2" class="flex-1 hidden">
                     <h2 class="text-2xl font-semibold mb-4 text-gray-800 border-b pb-2">🗄️ ตั้งค่าฐานข้อมูลและเมล</h2>
                     
                     <div class="space-y-4">
                        <div class="bg-blue-50 p-4 rounded-lg border border-blue-100 mb-2">
                             <h3 class="text-sm font-semibold text-blue-800 mb-2">ระบบฐานข้อมูล (MariaDB)</h3>
                             <div>
                                 <label class="block text-xs font-medium text-gray-700 mb-1">รหัสผ่าน Root (MySQL) <span class="text-red-500">*</span></label>
                                 <input type="password" id="MYSQL_ROOT_PASSWORD" name="MYSQL_ROOT_PASSWORD" required
                                     class="w-full px-3 py-2 text-sm rounded-md border border-gray-300 focus:ring-1 focus:ring-blue-500">
                             </div>
                             <div class="flex space-x-3 mt-3">
                                 <div class="w-1/2">
                                     <label class="block text-xs font-medium text-gray-700 mb-1">ชื่อผู้ใช้ฐานข้อมูล (User)</label>
                                     <input type="text" id="MYSQL_USER" name="MYSQL_USER" value="astro" required
                                         class="w-full px-3 py-2 text-sm rounded-md border border-gray-300 focus:ring-1 focus:ring-blue-500">
                                 </div>
                                 <div class="w-1/2">
                                     <label class="block text-xs font-medium text-gray-700 mb-1">รหัสผ่าน (Password) <span class="text-red-500">*</span></label>
                                     <input type="password" id="MYSQL_PASSWORD" name="MYSQL_PASSWORD" required
                                         class="w-full px-3 py-2 text-sm rounded-md border border-gray-300 focus:ring-1 focus:ring-blue-500">
                                 </div>
                             </div>
                        </div>

                        <div class="bg-gray-50 p-4 rounded-lg border border-gray-100">
                            <h3 class="text-sm font-semibold text-gray-600 mb-2">อีเมลระบบแจ้งเตือน (SMTP - Optional)</h3>
                            <div class="flex space-x-3">
                                 <div class="w-1/2">
                                     <label class="block text-xs font-medium text-gray-700 mb-1">อีเมลผู้ส่ง (Username)</label>
                                     <input type="email" id="MAIL_USERNAME" name="MAIL_USERNAME" value="learn2earn@bde.go.th"
                                         class="w-full px-3 py-2 text-sm rounded-md border border-gray-300">
                                 </div>
                                 <div class="w-1/2">
                                     <label class="block text-xs font-medium text-gray-700 mb-1">App Password</label>
                                     <input type="password" id="MAIL_PASSWORD" name="MAIL_PASSWORD" value="inljvvpjdtsvglwn"
                                         class="w-full px-3 py-2 text-sm rounded-md border border-gray-300">
                                 </div>
                             </div>
                        </div>
                     </div>

                    <div class="mt-6 flex justify-between">
                        <button type="button" onclick="nextStep(1)" class="px-5 py-2 text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg transition-colors">
                            ย้อนกลับ
                        </button>
                        <button type="submit" id="installBtn" class="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg shadow-md transition-colors flex items-center">
                            🚀 เริ่มติดตั้งและรันระบบ
                        </button>
                    </div>
                </div>

                <!-- Step 3: Deployment Progress -->
                <div id="step-3" class="flex-1 hidden flex-col">
                    <h2 class="text-2xl font-semibold mb-2 text-gray-800">⚡ กำลังดำเนินการติดตั้ง...</h2>
                    <p class="text-sm text-gray-500 mb-4">ระบบกำลังสร้างไฟล์ตั้งค่า โหลด Docker Image และเตรียมฐานข้อมูล กรุณารอสักครู่ (อาจใช้เวลา 3-5 นาที)</p>
                    
                    <div id="terminal-container" class="terminal flex-1 rounded-lg p-4 overflow-y-auto text-xs sm:text-sm h-64 md:h-auto shadow-inner relative">
                        <div id="terminal-output">รอรับคำสั่ง...</div>
                    </div>

                    <div id="success-message" class="hidden mt-6 bg-green-50 border border-green-200 text-green-800 p-4 rounded-xl flex items-start space-x-3">
                        <svg class="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        <div>
                            <h3 class="font-bold text-lg">ติดตั้งเสร็จสมบูรณ์!</h3>
                            <p class="text-sm opacity-90 mt-1">คุณสามารถปิดหน้านี้และล็อกอินเข้าระบบได้ที่:</p>
                            <a href="#" id="final-link" target="_blank" class="inline-block mt-2 font-mono bg-white px-3 py-1 rounded shadow-sm text-blue-600 hover:underline"></a>
                        </div>
                    </div>
                </div>

            </form>
        </div>
    </div>

    <script>
        function toggleSSLFields() {
            const sslFields = document.getElementById('ssl-fields');
            const isEnabled = document.getElementById('ENABLE_SSL').checked;
            if(isEnabled) {
                sslFields.classList.remove('hidden');
                document.getElementById('SSL_CERT_PATH').required = true;
                document.getElementById('SSL_KEY_PATH').required = true;
                document.getElementById('FRONTEND_PORT').value = "443";
            } else {
                sslFields.classList.add('hidden');
                document.getElementById('SSL_CERT_PATH').required = false;
                document.getElementById('SSL_KEY_PATH').required = false;
                document.getElementById('FRONTEND_PORT').value = "3001";
            }
        }

        function nextStep(step) {
            // Validation
            if(step == 2) {
                if(!document.getElementById('SERVER_IP').value) {
                    alert('กรุณาระบุ IP ของเซิร์ฟเวอร์'); return;
                }
            }
            
            // Hide all
            document.getElementById('step-1').classList.add('hidden');
            document.getElementById('step-2').classList.add('hidden');
            document.getElementById('step-3').classList.add('hidden');
            
            // Show target
            document.getElementById('step-' + step).classList.remove('hidden');
            
            // Update markers
            if(step == 2) {
                document.getElementById('step-2-marker').classList.remove('opacity-50');
                document.getElementById('step-2-marker').querySelector('span').classList.add('bg-white', 'text-blue-600');
            } else if (step == 3) {
                document.getElementById('step-3-marker').classList.remove('opacity-50');
                document.getElementById('step-3-marker').querySelector('span').classList.add('bg-white', 'text-blue-600');
            }
        }

        document.getElementById('setupForm').addEventListener('submit', function(e) {
            e.preventDefault();
            nextStep(3);
            
            const formData = new FormData(this);
            const data = Object.fromEntries(formData.entries());
            
            // Send config to backend
            fetch('/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            }).then(response => {
                if(response.ok) {
                    startLogStream(data.SERVER_IP, data.FRONTEND_PORT);
                } else {
                    document.getElementById('terminal-output').innerHTML += "<br><span style='color:red'>เกิดข้อผิดพลาดในการส่งคำสั่ง</span>";
                }
            }).catch(err => {
                document.getElementById('terminal-output').innerHTML += "<br><span style='color:red'>Network Error: " + err + "</span>";
            });
        });

        function startLogStream(ip, port) {
            const terminal = document.getElementById('terminal-output');
            const termContainer = document.getElementById('terminal-container');
            terminal.innerHTML = "กำลังเชื่อมต่อกับ Service...<br>";

            const eventSource = new EventSource('/logs');
            
            eventSource.onmessage = function(event) {
                if (event.data === "DONE_SUCCESS") {
                    eventSource.close();
                    document.getElementById('success-message').classList.remove('hidden');
                    const link = document.getElementById('final-link');
                    let cleanIp = ip.replace('http://', '').replace('https://', '').split('/')[0];
                    let protocol = document.getElementById('ENABLE_SSL').checked ? "https://" : "http://";
                    let finalUrl = protocol + cleanIp + ":" + port;
                    if ((protocol === "https://" && port == "443") || (protocol === "http://" && port == "80")) {
                        finalUrl = protocol + cleanIp;
                    }
                    link.href = finalUrl;
                    link.innerText = finalUrl;
                    terminal.innerHTML += "<br><span style='color:#00ff00; font-weight:bold'>[SYSTEM] ระบบพร้อมใช้งานแล้ว!</span>";
                } else if (event.data === "DONE_ERROR") {
                    eventSource.close();
                    terminal.innerHTML += "<br><span style='color:red; font-weight:bold'>[SYSTEM] เกิดข้อผิดพลาดระหว่างติดตั้ง กรุณาดู Log</span>";
                } else {
                    // escape HTML safely
                    const div = document.createElement('div');
                    div.innerText = event.data;
                    terminal.appendChild(div);
                    // auto scroll to bottom
                    termContainer.scrollTop = termContainer.scrollHeight;
                }
            };

            eventSource.onerror = function() {
                eventSource.close();
            };
        }
    </script>
</body>
</html>
"""

def write_env(data):
    # Sanitize SERVER_IP
    server_ip = data.get('SERVER_IP', 'localhost').strip()
    server_ip = server_ip.replace('http://', '').replace('https://', '').split('/')[0]
    
    # SSL Configuration
    use_ssl = data.get('ENABLE_SSL') == 'on'
    ssl_cert_path = data.get('SSL_CERT_PATH', '')
    ssl_key_path = data.get('SSL_KEY_PATH', '')
    protocol = "https" if use_ssl else "http"

    # Prepare the env content using the provided form data
    # Use quotes for all values to be safe
    env_content = f"""# --- Database Configuration ---
MYSQL_ROOT_PASSWORD='{data.get('MYSQL_ROOT_PASSWORD', 'rootpassword')}'
MYSQL_DATABASE='psu_backend'
MYSQL_USER='{data.get('MYSQL_USER', 'astro')}'
MYSQL_PASSWORD='{data.get('MYSQL_PASSWORD', 'password123')}'
MYSQL_PORT_EXTERNAL=3307

# --- Backend Configuration ---
BACKEND_PORT_EXTERNAL='{data.get('BACKEND_PORT', '3000')}'
MAIL_SERVER='{data.get('MAIL_SERVER', 'smtp.gmail.com')}'
MAIL_PORT='{data.get('MAIL_PORT', '465')}'
MAIL_USERNAME='{data.get('MAIL_USERNAME', 'learn2earn@bde.go.th')}'
MAIL_PASSWORD='{data.get('MAIL_PASSWORD', 'inljvvpjdtsvglwn')}'
MAIL_USE_SSL='true'
MAIL_FROM='Intelligist DataX <{data.get('MAIL_USERNAME', 'learn2earn@bde.go.th')}>'

# --- Frontend Configuration ---
FRONTEND_PORT_EXTERNAL='{data.get('FRONTEND_PORT', '3001')}'
SERVER_IP='{server_ip}'
FRONTEND_URL='{protocol}://{server_ip}:{data.get('FRONTEND_PORT', '3001')}'

# --- SSL Configuration ---
USE_SSL='{'true' if use_ssl else 'false'}'
SSL_CERT_PATH='{ssl_cert_path}'
SSL_KEY_PATH='{ssl_key_path}'
"""
    with open(ENV_FILE, 'w') as f:
        f.write(env_content)


def execute_deployment():
    # 0. Handle Nginx Config for SSL
    try:
        env_vars = {}
        if os.path.exists(ENV_FILE):
            with open(ENV_FILE, 'r') as f:
                for line in f:
                    if '=' in line:
                        k, v = line.strip().split('=', 1)
                        env_vars[k] = v.strip("'")

        if env_vars.get('USE_SSL') == 'true':
            if os.path.exists("frontend/nginx.ssl.conf"):
                with open("frontend/nginx.ssl.conf", 'r') as src:
                    with open("frontend/nginx.conf", 'w') as dst:
                        dst.write(src.read())
                with open(LOG_FILE, 'a') as f: f.write("[SYSTEM] ตั้งค่า Nginx สำหรับ SSL เรียบร้อยแล้ว\n")
        else:
            # Revert to standard if needed (assuming we have a backup or a standard template)
            # For simplicity, we assume nginx.conf is standard unless we change it.
            # In a real scenario, we might want to keep nginx.standard.conf
            pass
    except Exception as e:
        with open(LOG_FILE, 'a') as f: f.write(f"[WARNING] ไม่สามารถตั้งค่า Nginx: {str(e)}\n")

    with open(LOG_FILE, 'a') as f:
        f.write("[SYSTEM] สร้างไฟล์ .env เรียบร้อยแล้ว\n")
    
    # 0. Load Offline Docker Images if they exist
    if os.path.exists("backend.tar"):
        with open(LOG_FILE, 'a') as f: f.write("[SYSTEM] กำลังโหลดอิมเมจระบบ Backend (Offline)...\n")
        subprocess.run(["docker", "load", "-i", "backend.tar"])
    
    if os.path.exists("frontend.tar"):
        with open(LOG_FILE, 'a') as f: f.write("[SYSTEM] กำลังโหลดอิมเมจระบบ Frontend (Offline)...\n")
        subprocess.run(["docker", "load", "-i", "frontend.tar"])

    with open(LOG_FILE, 'a') as f: f.write("[SYSTEM] เริ่มดำเนินการสร้าง Container...\n")

    # Command 1: docker-compose up
    try:
        # Use the standard docker-compose.yml for source code build
        compose_file = "docker-compose.yml"
        compose_cmd = ["docker-compose", "-f", compose_file, "up", "-d", "--build"]

        process = subprocess.Popen(
            compose_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Merge stderr into stdout
            text=True
        )
        for line in iter(process.stdout.readline, ''):
            with open(LOG_FILE, 'a') as f:
                f.write(line)
        process.stdout.close()
        process.wait()
        
        if process.returncode != 0:
            with open(LOG_FILE, 'a') as f:
                f.write("[ERROR] Docker compose ล้มเหลว\n")
                f.write("DONE_ERROR\n")
            return

        with open(LOG_FILE, 'a') as f:
            f.write("[SYSTEM] Docker Containers สร้างเสร็จเรียบร้อยแล้ว\n")
            f.write("[SYSTEM] กำลังเตรียมฐานข้อมูล (รอ 10 วินาทีเพื่อให้ MariaDB พร้อม)...\n")
        
        # Command 2: Database Init
        db_process = subprocess.Popen(
            ["bash", "init_db_uat.sh"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in iter(db_process.stdout.readline, ''):
            with open(LOG_FILE, 'a') as f:
                f.write(line)
        db_process.stdout.close()
        db_process.wait()

        with open(LOG_FILE, 'a') as f:
            f.write("[SYSTEM] สร้างฐานข้อมูลเสร็จสิ้นกระบวนการทั้งหมด\n")
            f.write("DONE_SUCCESS\n")

    except Exception as e:
        with open(LOG_FILE, 'a') as f:
            f.write(f"[ERROR] คำสั่งล้มเหลวร้ายแรง: {str(e)}\n")
            f.write("DONE_ERROR\n")


class SetupHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(UI_HTML.encode('utf-8'))
        elif self.path == '/logs':
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'text/event-stream; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.end_headers()
            
            # Very simple tail implementation
            try:
                with open(LOG_FILE, 'r') as f:
                    # Read what's already there
                    lines = f.readlines()
                    for line in lines:
                        self.wfile.write(f"data: {line.strip()}\n\n".encode('utf-8'))
                        self.wfile.flush()
                    
                    # Follow new lines continuously
                    while True:
                        where = f.tell()
                        line = f.readline()
                        if not line:
                            import time
                            time.sleep(1)
                            f.seek(where)
                        else:
                            stripped_line = line.strip()
                            self.wfile.write(f"data: {stripped_line}\n\n".encode('utf-8'))
                            self.wfile.flush()
                            if stripped_line in ["DONE_SUCCESS", "DONE_ERROR"]:
                                break
            except BrokenPipeError:
                pass # Client disconnected

        else:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")

    def do_POST(self):
        if self.path == '/start':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data_dict = json.loads(post_data.decode('utf-8'))
                
                # Setup Environment
                write_env(data_dict)
                
                # Clear log before starting
                open(LOG_FILE, 'w').close()
                
                # Kick off deployment thread
                install_thread = threading.Thread(target=execute_deployment)
                install_thread.start()
                
                self.send_response(HTTPStatus.OK)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "ok"}')
            except Exception as e:
                self.send_response(HTTPStatus.BAD_REQUEST)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

if __name__ == "__main__":
    # Remove existing .env and logs if present to ensure clean state
    if os.path.exists(LOG_FILE): os.remove(LOG_FILE)
    
    handler = SetupHTTPRequestHandler
    with socketserver.TCPServer(("0.0.0.0", PORT), handler) as httpd:
        print(f"============================================================")
        print(f"  UI Setup Server กำลังทำงาน...")
        print(f"  กรุณาเปิดเบราว์เซอร์ไปที่: http://localhost:{PORT}")
        print(f"============================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nปิดการทำงาน Setup Server")
