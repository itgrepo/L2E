# L2E API Management Static Audit Report

## 1. Repository Baseline
- **Repository path**: `/Users/natthawutjantakul/intelligist_dataX`
- **Current branch**: `main`
- **Current commit hash**: `72e86d04de280e7314b159305009287afd95e48b`
- **git status**: On branch main, up to date with origin/main.
- **Uncommitted files**: มีไฟล์ Modified ~38 ไฟล์ (เช่น `bigdataservice.py`, `APIManagementView.vue`) และ Untracked files จำนวนมากที่เกิดจากการทำงานก่อนหน้านี้
- **Relevant commits**: ไม่ได้ระบุถึง Commit ล่าสุดเจาะจง แต่ Working Tree ปัจจุบันมีโค้ด API Management รวมอยู่แล้ว
- **Frontend path**: `frontend/` (Vue 3, Vite)
- **Backend path**: `backendold/Astro_backend/` (Python Flask)
- **Database technology**: MySQL/MariaDB
- **Build/Test commands**: `npm run build` (Frontend), `python run.py` (Backend)
- **Environment ที่สามารถใช้ทดสอบได้**: Local environment ที่ตั้งค่า Database ไว้ตรงกับ `intelligist_datax_full_dump.sql`

## 2. API Configuration
- **Endpoints**: 
  - `/getAvailableDatabases`
  - `/getAvailableTables`
  - `/getTableColumns`
  - `/saveApiConfig`
- **สถานะ**: มีอยู่จริงใน `bigdataservice.py` (บรรทัด 810-944)
- **การตรวจสอบการทำงาน**:
  - Frontend นำไปเรียกใช้งานจริง และไม่ใช่ Mock Data
  - สามารถอ่านรายชื่อ Table, View, และ Column จากฐานข้อมูลจริงโดย query ผ่าน `INFORMATION_SCHEMA`
  - ข้อมูล Configuration ถูกบันทึกลงใน Table `service` (เช่น `api_enabled`, `api_db_name`, `api_source_name`, `api_request_fields`, `api_response_fields`)
  - Config นี้ถูกดึงไปใช้จริงโดย Data Plane Runtime (`/dataapi/api/v1/<dataset_id>`) 

## 3. Credential Management
- **Endpoints**:
  - `/addApiCredential` (สร้าง Credential ใหม่)
  - `/extendApiCredential` (แก้ไข Expires_at)
  - `/revokeApiCredential` (ตั้ง `status` = 'revoked')
  - `/resumeApiCredential` (ตั้ง `status` = 'active')
  - `/deleteApiCredential` (ลบ Credential + Scope ถาวร)
- **การตรวจสอบการทำงาน**:
  - Credential ผูกกับ `service_id` และ `target_user_id` จริงในตาราง `api_credentials`
  - Secret Key สร้างจากฝั่ง Backend หากไม่ได้ส่งมา (`uuid.uuid4().hex`)
  - Secret Key ถูกเก็บแบบ **Plaintext** ในฐานข้อมูล และ Response กลับเป็น Plaintext ใน endpoint `/getApiCredentials`
  - การ Pause ใช้ `/revokeApiCredential` เมื่อ `status != 'active'` Data Plane จะปฏิเสธ Request จริง
  - เมื่อ Resume แล้วสามารถกลับมาใช้ Key เดิมได้
  - การจัดการ Credential มีช่องโหว่ **Broken Access Control (IDOR)** (ดูข้อ 8 และ 11) ทำให้ผู้ที่ไม่ใช่ Admin อาจเรียกจัดการ Credential ได้

## 4. Scope Management
- **Endpoints**: `/saveApiScopeForUser`, `/deleteApiScopeForUser`, `/getAllApiScopes`
- **การตรวจสอบการทำงาน**:
  - Scope JSON ถูกเก็บใน `api_scopes.scope_json`
  - Backend Runtime มีการ Validation รองรับ Operator `['=', '!=', '>', '<', '>=', '<=', 'LIKE', 'IN']`
  - Field ถูก Validate ด้วย Regex `^[a-zA-Z0-9_]+$`
  - Scope ถูกประกอบเข้าไปใน `WHERE` clause ด้วยเงื่อนไข `AND/OR` และใช้ **Parameterized Query** (`%s`) จึงลดความเสี่ยง SQL Injection ตรงจุดนี้
  - สิทธิ์การแก้ไข Scope ถูกสร้างเงื่อนไขตรวจสอบแอดมินไว้ (ผ่าน `checkUserIsAdmin`)

## 5. Data Plane Runtime
- **Endpoint**: `@app.route('/dataapi/api/v1/<dataset_id>', methods=['GET'])` (บรรทัด 554 ใน `bigdataservice.py`)
- **กระบวนการทำงาน**:
  1. ค้นหา Configuration ผ่าน `dataset_id`
  2. ตรวจ `api_enabled`
  3. อ่าน API Key จาก **Query String** `?apikey=xxx` (ไม่ได้อ่านจาก Header `x-api-key` หรือ `Authorization`)
  4. ตรวจสถานะ `status == 'active'` ในตาราง `api_credentials`
  5. ตรวจ `expires_at < datetime.now()`
  6. ตรวจ `service_id` ตรงกัน
  7. Apply Request Fields (Exact Match)
  8. จำกัด Response Fields ตาม `api_response_fields`
  9. Apply Scope จาก `api_scopes`
  10. ทำ Parameterized Query ในส่วนเงื่อนไข
  11. Execute และ Return Data (สูงสุด 1000 แถว)
  12. บันทึก Access Log ผ่าน `log_api_usage`
- **ปัญหา**: ปิดบังข้อมูลในระดับหนึ่ง แต่ยังส่ง `str(e)` คืน Client เมื่อเกิด Exception อาจทำให้โครงสร้าง Database รั่วไหลได้

## 6. API-Level Pause
### API Configuration Status
- **Admin สามารถปิด API ทั้ง Endpoint ได้**: ผ่าน `api_enabled`
- **เมื่อปิดแล้ว**: Runtime จะคืนค่า HTTP 403 `API access is disabled for this dataset` ทำให้ Credential ทุกตัวของ API นั้นถูกปฏิเสธ
- **เปิดกลับมา**: Credential ข้อมูลยังอยู่ครบและทำงานต่อได้

### Credential Status
- **Pause เฉพาะ User**: ได้ผ่าน `/revokeApiCredential`
- **User อื่นของ API เดียวกัน**: ใช้งานได้ปกติ (Data Plane ตรวจสอบสถานะระดับ Credential)
- **Resume**: ใช้ `/resumeApiCredential` Key เดิมจะกลับมาใช้ได้ปกติ

## 7. Expiration
- **ข้อมูลถูกบันทึกที่ไหน**: `api_credentials.expires_at`
- **การบังคับใช้**: Data Plane ตรวจสอบ `if expires_at and expires_at < datetime.now():` ทุกครั้งที่มี Request ใหม่
- **Timezone**: ใช้เวลาเครื่อง Server ปัจจุบัน (`datetime.now()`)
- **Extend**: สามารถเพิ่มเวลาให้ Key ที่หมดอายุได้ผ่าน `/extendApiCredential`
- **ข้อมูล NULL**: หากไม่ได้กำหนดเวลา (NULL) ข้อมูลจะไม่มีวันหมดอายุ 

## 8. Authorization
- **การตรวจสอบฝั่ง Control Plane (Backend)**:
  มีการเขียนเงื่อนไขป้องกันใน `/saveApiConfig`, `/addApiCredential`, ฯลฯ ว่า:
  `if not user_data.get("user_id") and not checkUserIsAdmin(user_data): return jsonify({"status": "Permission Denied"})`
  **ปัญหา (Critical IDOR/Broken Access Control)**: ตรรกะผิดพลาดอย่างรุนแรง เนื่องจากหาก `user_id` มีค่า (เป็น User ธรรมดาที่ล็อกอิน) นิพจน์ `not user_data.get("user_id")` จะเป็น False ทำให้ `False AND ...` ได้ผลลัพธ์เป็น False ทันที บล็อก If นี้จึงไม่ทำงาน ส่งผลให้ **User ธรรมดาทุกคนสามารถเข้าถึงฟังก์ชันระดับแอดมินทั้งหมดได้**
- **การซ่อนปุ่ม**: ปัจจุบันระบบใช้การซ่อนปุ่มฝั่ง Frontend ทำให้ User ธรรมดามองไม่เห็น แต่ไม่ได้ช่วยป้องกันเรื่องความปลอดภัย

## 9. Audit และ Access Log
- **Control Plane Log (API Management)**:
  - **สร้าง/แก้ไข API**: ไม่มีการบันทึก
  - **แจก/Pause/Resume/Delete Credential**: ไม่มีการบันทึก
  - **แก้ไข Scope**: ไม่มีการบันทึก
- **Data Plane Log (Access Log)**:
  - **เรียก API สำเร็จ/ล้มเหลว**: มีการบันทึกผ่านฟังก์ชัน `log_api_usage` (ลงตาราง `log`) โดยเก็บ `user_id`, Status Code, Message, IP
- **สิ่งขาดหาย**: Control Plane ยังไม่มี Audit Log แบบเต็มรูปแบบที่ระบุว่าใครทำอะไร และ Data Plane Log ขาดการบันทึก Request ID และ User Agent

## 10. Database Mapping
- **API Configuration**: ตาราง `service`
  - Fields: `service_id` (PK), `api_enabled`, `api_type`, `api_endpoint`, `api_db_name`, `api_source_type`, `api_source_name`, `api_request_fields`, `api_response_fields`
- **API Credential**: ตาราง `api_credentials`
  - Fields: `credential_id` (PK), `service_id` (FK), `user_id` (FK), `secret_key`, `status`, `expires_at`, `created_at`
- **API Scope**: ตาราง `api_scopes`
  - Fields: `scope_id` (PK), `credential_id` (FK), `scope_json`
- **Log**: ตาราง `log`
  - Fields: `log_id` (PK), `user_id`, `ip`, `path`, `log_detail`, `type`, `time`, `country`

## 11. Security Review
- **Secret Management**: **CRITICAL** Secret Key สร้างและถูกเก็บเป็น Plaintext ในฐานข้อมูล รวมถึงเมื่อเรียก `/getApiCredentials` จะมีการคืนค่า Secret ของทุกคนกลับไปยัง Frontend ซึ่งเสี่ยงต่อการหลุดของ Key (Key Exposure)
- **Broken Access Control / IDOR**: **CRITICAL** User ธรรมดาสามารถข้ามสิทธิ์เพื่อสร้างและลบ Credential/API Config ได้จากตรรกะที่ผิดพลาดใน `if not user_data.get("user_id") and not checkUserIsAdmin(user_data):`
- **SQL Injection**: `api_db_name` ถูกตรวจด้วย Whitelist และตัวแปรใน WHERE/Scope ใช้ Parameterized Query ซึ่งถือว่าปลอดภัยระดับหนึ่ง แต่ `api_source_name` ไม่มีการบังคับ Validation เข้มงวดตอนใช้งาน (พึ่งพาเฉพาะ Backticks) 
- **Error Information Leakage**: มีการคืนค่า `str(e)` คืน Client เมื่อมี Exception อาจให้ข้อมูลโครงสร้างฐานข้อมูลที่อ่อนไหว

## 12. Status Matrix

| Capability | Status | Frontend | Backend Control Plane | Data Plane | Database | Runtime Enforcement | Evidence | Missing Work |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| API Configuration | IMPLEMENTED_UNVERIFIED | Yes | Yes | Yes | Yes | Yes | `saveApiConfig` | Validation table name |
| Credential Management | PARTIAL | Yes | Yes | N/A | Yes | N/A | `addApiCredential` | **Fix Broken Auth** / Hash Secret |
| Scope Management | IMPLEMENTED_UNVERIFIED | Yes | Yes | Yes | Yes | Yes | `api_scopes` parse | - |
| Data Plane Runtime | PARTIAL | N/A | N/A | Yes | N/A | Yes | `/dataapi/api/v1/<id>` | Use Header for API Key, Fix Info Leak |
| API-Level Pause | IMPLEMENTED_UNVERIFIED | Yes | Yes | Yes | Yes | Yes | `api_enabled` | - |
| Credential Pause | IMPLEMENTED_UNVERIFIED | Yes | Yes | Yes | Yes | Yes | `revokeApiCredential` | - |
| Expiration | IMPLEMENTED_UNVERIFIED | Yes | Yes | Yes | Yes | Yes | `extendApiCredential` | - |
| Authorization | PARTIAL (BROKEN) | Yes | **Broken** | N/A | N/A | No | `if not user_id and ...` | **Fix logic operator AND/OR** |
| Audit and Access Log| PARTIAL | N/A | No | Yes | Yes | Yes | `log_api_usage` | **Add Audit for Control Plane** |

## 13. Evidence
- **Data Plane (Execution)**: `bigdataservice.py`, Line 554 (`@app.route('/dataapi/api/v1/<dataset_id>')`)
- **Credential Auth Flaw**: `bigdataservice.py`, Line 991 (`if not user_data.get("user_id") and not checkUserIsAdmin(user_data):`)
- **Secret Plaintext Return**: `bigdataservice.py`, Line 953 (`SELECT c.secret_key ... FROM api_credentials`)
- **Access Log implementation**: `bigdataservice.py`, Line 567 (`def log_api_usage(...)`)

## 14. สรุป (Conclusion)
- **ส่วนใดมีอยู่แล้ว**: ระบบ UI (Control Plane) มีโครงสร้างครบถ้วน การผูก Dataset, กำหนด Scope และสร้าง Credential ทั้งหน้าเว็บและ API หลังบ้านทำมาเชื่อมต่อกันเสร็จแล้ว
- **Data Plane มีหรือไม่**: มีอยู่แล้วที่ `@app.route('/dataapi/api/v1/<dataset_id>')` ซึ่งบังคับใช้ Credential (API Key), การหมดอายุ, และ Scope อย่างถูกต้องด้วย Parameterized SQL
- **API Key ถูกบังคับใช้จริงหรือไม่**: **จริง** (แต่รองรับผ่าน URL Query String เท่านั้น ยังไม่อ่านจาก HTTP Header)
- **Scope ถูกบังคับใช้จริงหรือไม่**: **จริง**
- **Security Findings**: 
  - **(1)** ช่องโหว่ Broken Access Control รุนแรงมาก ทำให้ใครก็เข้าถึงฟังก์ชัน Admin ของส่วนนี้ได้ 
  - **(2)** Secret Key เก็บแบบ Plaintext ทั้งตอนอยู่บนฐานข้อมูลและถูกส่งผ่าน API ไปแสดงใน Frontend 
  - **(3)** การตอบกลับ Error จาก Data Plane รั่วไหลข้อมูล Stack Trace
- **Blockers / Missing Work**: ต้องอุดช่องโหว่การเช็คสิทธิ์ (Authorization) และพิจารณาปรับการเก็บ Secret เป็น Hash ก่อนเปิดให้ใช้งานจริง รวมถึงเพิ่ม Audit Log เวลาสร้างหรือแก้ไข Credential
- **คำถามที่ต้องตรวจต่อ**: ต้องการให้ผมเริ่มทำการ Fix ช่องโหว่ความปลอดภัยระดับ Critical ก่อน (Authorization + Secrets) หรือปรับเปลี่ยนให้ Data Plane รองรับ Header `Authorization: Bearer <API_KEY>` ก่อน?
