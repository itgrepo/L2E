# L2E_SYSTEM_GAPS_CURRENT_STATE_AUDIT

## 1. REPOSITORY BASELINE

- **Repository path**: `/Users/natthawutjantakul/intelligist_dataX`
- **Current branch**: `fix/l2e-full-responsive-uat`
- **Current commit hash**: `d587d08b83d7d0cce1dbfb37f50f4c914b3b1ad1`
- **Frontend path**: `frontend/`
- **Backend path**: `backendold/Astro_backend/`
- **Database technology**: MariaDB / MySQL (UAT `datax_db_3003`)
- **Router path**: `frontend/src/router` (Frontend), `backendold/Astro_backend/app/ServiceConfig/*.py` (Backend)
- **Migration path**: Not found (ไม่มี `migration` folder ใน codebase)
- **UAT deployment**: Docker container `datax_backend_3003` / `datax_frontend_3003` บน `134.185.172.127`

> **Note**: Evidence in this document is derived from DB schema queries on UAT, frontend source code inspection, and backend codebase structure.

---

## 2. SYSTEM GAP CLASSIFICATION

### Main System Gap Classification

| Gap | Capability Exists | L2E Structure Complete | L2E Master Data Present | Classification | Status | Evidence |
|---|---|---|---|---|---|---|
| GAP-01 L2E Dataset Group | ✅ มี Field Category แทน | ❌ โครงสร้างยังไม่แยกอิสระจาก Dataset Type | ❌ | SYSTEM | PARTIAL | UI: `DatasetConfigView.vue` (categoriesList), Backend: `category` ใน `service` table |
| GAP-02 Dataset ID Standard | ✅ มี Field `dataset_id` และตรวจ Duplicate | ❌ ขาดการ Validate Prefix `CRS-`, `CMP-` ฯลฯ | ❌ | SYSTEM | PARTIAL | Backend: `addService` ใน `bigdataservice.py` บันทึกและเช็คซ้ำ แต่ไม่ Validate Prefix |
| GAP-03 Source System | ✅ มี Field text `data_source` | ❌ ขาด Master Table, Dropdown และ FK Validation | ❌ | SYSTEM | PARTIAL | DB: `service.data_source`, Backend: `addService` เซฟเป็น Free text |
| GAP-04 Data Sensitivity | ✅ มี Field `access_type` (สาธารณะ/ภายใน) | ❌ ขาด Restricted / PII | ❌ | SYSTEM | PARTIAL | DB: `service.access_type`, UI: Dropdown ใน `DatasetConfigView.vue` |
| GAP-05 Permission Linked | ✅ มี `service_group_access` | ❌ ยังไม่ผูกเข้ากับ Sensitivity PII อัตโนมัติ | ❌ | SYSTEM | PARTIAL | Backend: `get_dataset_api` บล็อคตามสิทธิ์ แต่ไม่ได้เช็คจากระดับ Sensitivity |
| GAP-06 API Service Binding | ✅ ผูกแบบ 1:1 ภายใน Record เดียว | ⚠️ รองรับแค่ 1:1 Model, ยังไม่เป็น Registry แยก | ❌ | MIXED | PARTIAL | DB: Table `service` เก็บทั้ง Dataset Metadata และ API Config (`api_endpoint`) ไว้ด้วยกัน |
| GAP-07 Dataset Template | ❌ ไม่มีระบบ Template | ❌ ขาดระบบ Template และ Dynamic Validation | ❌ | SYSTEM | NOT_FOUND | ไม่มี Code/Schema ใน Backend ที่รองรับ Template Validation ตามหมวดหมู่ข้อมูล |
| GAP-08 Organization Schema | ✅ มีหน้า Management, API, DB ครบ | ❌ ขาด Field L2E (Type, Role, Contact, Owner) | ❌ | MIXED | PARTIAL | UI: `OrganizationManagementView.vue`, DB: `organization` ขาดฟิลด์เพิ่มเติม |
| GAP-09 Label/Help Text | ✅ มี Label พื้นฐาน | ❌ คำอธิบายไม่ตรงและไม่ครอบคลุม L2E | ❌ | UX/DOCUMENTATION | PARTIAL | UI: ขาด Placeholder และ Guideline ที่ชัดเจนใน `DatasetConfigView.vue` |
| GAP-10 Backend Master Validation | ❌ ไม่มีการ Validate | ❌ Backend รับ Master ID ปลอมได้โดยไม่เช็ค FK | ❌ | SYSTEM | NOT_FOUND | Backend: `addService` ไม่เช็ค `organization` หรือ `category` กับ Master Tables ก่อน Save |
| GAP-11 UI/Functional Bugs | ✅ ส่วนใหญ่หน้าจอทำงานได้ | ❌ บัคบางส่วนยังตกค้าง เช่น Favorites, Scrollbar | ❌ | BUG | PARTIAL | UI: Double Scrollbar และ State ของ Favorites ยังมีปัญหา |

### Supporting Master Data / Configuration Tasks

| Master | Management UI | CRUD API | DB Table | รองรับ Add | มีข้อมูล L2E | Classification |
|---|---|---|---|---|---|---|
| Category/Subcategory | ❌ ไม่มีแยก (Hardcode ใน UI) | ✅ `category_service.py` | ✅ `category` | ✅ | ❌ | MIXED |
| Organization | ✅ `OrganizationManagementView.vue` | ✅ `organization_service.py` | ✅ `organization` | ✅ | ❌ | MIXED |
| API Service | ✅ `APIManagementView.vue` | ✅ `bigdataservice.py` | ✅ `service` | ✅ | ❌ | CONFIG_ONLY |
| User/Role | ✅ `UserManagementView.vue` | ✅ `usersMgmt.py` | ✅ `user` | ✅ | ❌ | CONFIG_ONLY |
| Dataset | ✅ `DatasetManagementView.vue` | ✅ `bigdataservice.py` | ✅ `service` | ✅ | ❌ | CONFIG_ONLY |
| Source System | ❌ ไม่มี | ❌ ไม่มี | ❌ ไม่มี Master | ❌ | ❌ | SYSTEM / NOT_FOUND |

---

## 3. CLARIFICATION OF MIXED WORK

สำหรับ Gap ที่มีการผสมผสานระหว่างระบบและข้อมูล (MIXED) จะถูกแบ่งการทำงานตาม Dependency Order ดังนี้:

### GAP-01: L2E Dataset Group
- **System development required**: Dev ต้องเพิ่ม L2E Dataset Group field, การอัปเดต Schema และการ Validation ใน API.
- **Master data/configuration required**: BA/Admin ต้องทำการเพิ่มค่ากลุ่ม L2E (เช่น Course, Competency) เข้าไปในระบบหลังจากที่ Dev ทำการพัฒนาระบบเสร็จแล้ว.
- **Dependency order**: System development -> Master data configuration.

### GAP-03: Source System
- **System development required**: ปัจจุบันมี `data_source` เป็น text ธรรมดาอยู่แล้ว ต้องพัฒนาระบบเพิ่มเติมเพื่อสร้าง Source System Master, FK Constraint, Dropdown ใน UI และ Backend Validation.
- **Master data/configuration required**: BA/Admin เพิ่มระบบต้นทาง (Source Systems) ที่ใช้งานจริงเข้าสู่ Master Table.
- **Dependency order**: System development -> Master data configuration.

### GAP-06: API Service Binding
- **Product Decision Required**: โครงสร้างปัจจุบันนำ Dataset และ API มัดรวมกันแบบ 1:1 ภายใน `service` table ต้องให้ Product Owner ตัดสินใจเลือกระหว่าง:
  1. ใช้ 1:1 model ใน `service` table ต่อไป (ลดความซับซ้อน แต่ผูกขาด 1 Dataset ต่อ 1 API).
  2. แยก API Service Registry และ Mapping Table (รองรับ 1 Dataset ต่อหลาย APIs หรือใช้ Service ซ้ำ).
- **ข้อควรระวัง**: ⚠️ ห้ามเริ่มแก้ GAP-06 จนกว่า Product Owner จะตัดสินใจ.

### GAP-08: Organization Schema
- **System development required**: **ไม่ต้องสร้าง Organization Module ใหม่**. ให้ขยาย Module เดิม (`organization` table, `organization_service.py`, `OrganizationManagementView.vue`) โดยเพิ่ม Field: Type, Role, Contact, Owner, Active Flag และ Source System relation.
- **Master data/configuration required**: BA/Admin เข้าไปเพิ่มข้อมูล Organization ของฝั่ง L2E ตามโครงสร้างใหม่.
- **Dependency order**: System development (Schema Extension) -> Master data configuration.

---

## 4. SUMMARY (CLASSIFICATION COUNTS)

- **SYSTEM**: 7
- **MIXED**: 2
- **BUG**: 1
- **UX/DOCUMENTATION**: 1
- **Total**: 11

### STATUS COUNTS
- **DONE**: 0
- **IMPLEMENTED_UNVERIFIED**: 0
- **PARTIAL**: 9 (GAP-01, GAP-02, GAP-03, GAP-04, GAP-05, GAP-06, GAP-08, GAP-09, GAP-11)
- **CONFIG_ONLY**: 0 (สำหรับ Gaps หลัก)
- **NOT_FOUND**: 2 (GAP-07, GAP-10)
- **BLOCKED**: 0
