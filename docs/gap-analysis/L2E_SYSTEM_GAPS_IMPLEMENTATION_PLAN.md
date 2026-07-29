# L2E_SYSTEM_GAPS_IMPLEMENTATION_PLAN

## 1. IMPLEMENTATION WAVES

การดำเนินการแก้ไข System Gaps จะถูกแบ่งออกเป็นช่วง (Waves) เพื่อลดความเสี่ยงและจัดลำดับความสำคัญตามความปลอดภัย โครงสร้างหลัก และ UX

### Wave 0 — Preserve Baseline
- **แยก Branch**: ตัด branch ใหม่จาก responsive branch ปัจจุบัน (`fix/l2e-full-responsive-uat`).
- **บันทึก Working Tree**: รวบรวมการแก้ไขที่ยังไม่ได้ Commit ทั้งหมด.
- **ข้อควรระวัง**:
  - ⚠️ ห้าม `git add .` เด็ดขาด.
  - ⚠️ ห้ามนำไฟล์ `test-results`, `keys` (เช่น ubuntuL2E.key), `scripts` หรือ generated files รวบเข้า Commit โดยไม่ได้ตรวจสอบอย่างละเอียด.

### Wave 1 — Security and Validation
- **GAP-04**: Data Sensitivity (เพิ่ม Restricted, PII)
- **GAP-05**: Permission Enforcement (ผูก Role เข้ากับการปกป้อง PII/Restricted โดยอัตโนมัติ)
- **GAP-10**: Backend Master Validation (ป้องกัน ID ปลอมสำหรับ Category/Organization/Source System)

### Wave 2 — L2E Core Metadata
- **GAP-01**: L2E Dataset Group (สร้างฟิลด์แยกสำหรับระบบ L2E โดยเฉพาะ)
- **GAP-02**: Dataset ID Standard (เพิ่ม Prefix Validator ก่อน Save/Update)
- **GAP-03**: Source System (สร้าง Master Module และผูก FK เข้าสู่ Dataset)
- **GAP-08**: Organization Extension (ขยาย Module ปัจจุบันด้วย Type, Role, Contact, Owner, Active และ Source System relation)

### Wave 3 — Architecture and Templates
- **GAP-06**: API Service Binding (⚠️ **รอดำเนินการหลัง Product Decision**)
- **GAP-07**: Dataset Template (พัฒนาระบบ Schema/Template สำหรับแต่ละ Data Group พร้อม Dynamic Form Validation)

### Wave 4 — UX and Bugs
- **GAP-09**: Label/Help Text (ปรับปรุงคำอธิบายใน UI ทั้งหมดให้ครอบคลุมบริบท L2E)
- **GAP-11**: Favorites and Responsive Bugs (แก้ไขบัคการทำงานของ Favorites และปัญหา Double Scrollbar)

---

## 2. IMPLEMENTATION BACKLOG

### GAP-01: L2E Dataset Group
- **Current capability**: ใช้ `category` ฟิลด์เดิมใน `service` table โดย Frontend Hardcode ค่าไว้.
- **Missing system work**: เพิ่ม column แยก, สร้าง Dropdown L2E Group, เพิ่มการตรวจสอบ Validation ข้อมูลขาเข้า.
- **Missing configuration work**: BA ต้องกำหนดชุด Master Data สำหรับ L2E Dataset Group.
- **Frontend files**: `DatasetConfigView.vue`
- **Backend files**: `bigdataservice.py` (`addService`, `get_dataset_api`)
- **Database changes**: Add column `l2e_group_id` หรือ `l2e_group` (VARCHAR) ใน `service` table.
- **Migration**: เติมค่าเริ่มต้นให้ข้อมูลเดิมเป็น `general` เพื่อไม่ให้พัง.
- **Backward compatibility**: ข้อมูลเก่าใช้งานได้ปกติ.
- **Dependencies**: -
- **Acceptance criteria**: ผู้ใช้เลือก L2E Dataset Group จาก Dropdown ได้ และระบบจัดเก็บข้อมูลใน Backend ถูกต้อง.
- **Testing**: Unit (Yes), Integration (Yes), Browser (UI check).
- **Estimate**: S
- **Deployment risk**: Low

### GAP-02: Dataset ID Standard
- **Current capability**: มีฟิลด์ `dataset_id` และตรวจ Duplicate แล้ว.
- **Missing system work**: เพิ่ม Prefix Validator (Regex) ฝั่ง Frontend และ Backend. สร้างตัวคุมการซ้อนทับแบบ Lock.
- **Missing configuration work**: -
- **Frontend files**: `DatasetConfigView.vue`
- **Backend files**: `bigdataservice.py` (`addService`)
- **Database changes**: -
- **Migration**: -
- **Backward compatibility**: ข้อมูลเก่าที่มี ID รูปแบบเดิมต้องยังใช้งานได้.
- **Dependencies**: GAP-01 (หาก Prefix ต้องอิงตาม L2E Group).
- **Acceptance criteria**: กรอก Dataset ID ผิด Prefix ระบบจะปฏิเสธ (400) พร้อมข้อความที่ชัดเจน.
- **Testing**: Unit (Regex test), Integration (Save flow), Browser (Form feedback).
- **Estimate**: S
- **Deployment risk**: Low

### GAP-03: Source System
- **Current capability**: เก็บเป็น `data_source` Text ธรรมดา.
- **Missing system work**: สร้าง CRUD API/UI สำหรับ Master Source System, แก้ไข Dataset API ให้รับ ID แทน Text พร้อมเช็ค FK.
- **Missing configuration work**: Admin เพิ่มรายชื่อระบบต้นทางเข้าสู่ Master Table.
- **Frontend files**: หน้า Management ใหม่ หรือแก้ `DatasetConfigView.vue`
- **Backend files**: สร้าง `source_system_service.py`, แก้ `bigdataservice.py`
- **Database changes**: สร้าง Table `source_system`, ทำ FK จาก `service` table.
- **Migration**: ดึงข้อมูล `data_source` เก่ามาแยกบันทึกเป็น Master หรือเปลี่ยนเป็น ID อัตโนมัติ (ขึ้นอยู่กับ Business Logic).
- **Backward compatibility**: API เก่ายังต้องคืนค่าเป็นชื่อต้นทางให้ได้.
- **Dependencies**: -
- **Acceptance criteria**: ผูกระบบต้นทางกับ Dataset ได้ผ่าน Dropdown และรับประกันความถูกต้องด้วย Master Table.
- **Testing**: Unit (Model validation), Integration (API Linkage).
- **Estimate**: M
- **Deployment risk**: Medium

### GAP-04 & GAP-05: Data Sensitivity and Permission Enforcement
- **Current capability**: มีเพียง Public/Internal และเช็ค Permission กลุ่มแบบพื้นฐาน.
- **Missing system work**: ขยาย `access_type` (ENUM), เขียน Middleware ใน `get_dataset_api` ดัก PII/Restricted ว่า User มีสิทธิ์ Approval/Consent ถึงจะอนุญาต.
- **Missing configuration work**: -
- **Frontend files**: `DatasetConfigView.vue` (Sensitivity Dropdown)
- **Backend files**: `bigdataservice.py` (Validation & Authorization check)
- **Database changes**: อัปเดต Column ENUM หรือ Validation rule ของ `access_type`.
- **Migration**: ไม่จำเป็น (ข้อมูลเก่าตีความตามเดิม).
- **Backward compatibility**: -
- **Dependencies**: User Role module ต้องรองรับการให้ Approval สิทธิ์ชั้นสูง.
- **Acceptance criteria**: User ธรรมดาที่ร้องขอข้อมูล PII จะได้รับ 403 Forbidden เสมอ หากไม่มี Approval.
- **Testing**: Unit (Permission matrix), Integration (API 403 check).
- **Estimate**: M
- **Deployment risk**: High (Security)

### GAP-06: API Service Binding
- **Current capability**: ผูกรวม 1:1 ใน `service` table (Dataset กับ API ถือเป็น Record เดียวกัน).
- **Missing system work**: (รอ Product Decision) หากแยก Registry: สร้าง Table `api_registry`, Mapping Table `dataset_api_mapping`, ปรับแก้ Frontend UI.
- **Missing configuration work**: สร้าง Data Services.
- **Frontend files**: `APIManagementView.vue`, `DatasetManagementView.vue`
- **Backend files**: `bigdataservice.py` (Refactor query/logic ทั้งชุด)
- **Database changes**: รื้อโครงสร้างตาราง (High risk)
- **Migration**: นำ API เดิมแยกออกไปใส่ Table ใหม่ และผูก FK.
- **Backward compatibility**: ต้อง Maintain `getService` API ให้ทำงานแบบเดิมได้.
- **Dependencies**: Product Owner Approval.
- **Acceptance criteria**: API Binding ตรงกับ Decision ของ Product Owner.
- **Testing**: Integration Tests อย่างเข้มข้นใน Data Plane.
- **Estimate**: L
- **Deployment risk**: High

### GAP-07: Dataset Template
- **Current capability**: ไม่มี.
- **Missing system work**: สร้าง Schema Validator, UI Rendering engine ฝั่ง Frontend ดึง Template ตามหมวด.
- **Missing configuration work**: BA ระบุฟิลด์ที่บังคับ (Required) สำหรับแต่ละกลุ่มข้อมูล L2E.
- **Frontend files**: `DatasetConfigView.vue` (Dynamic Form)
- **Backend files**: `bigdataservice.py` (Payload schema validation)
- **Database changes**: เก็บ Template schema เป็น JSON ใน Table หรือใน Config.
- **Migration**: -
- **Backward compatibility**: Dataset เก่าไม่ต้องตรวจ Required Fields เพิ่ม.
- **Dependencies**: GAP-01.
- **Acceptance criteria**: เมื่อเลือก Course L2E Group ระบบจะบังคับให้กรอก Credit/Hours ทันที.
- **Testing**: Unit (Validation schema test), Browser (Form switching).
- **Estimate**: L
- **Deployment risk**: Medium

### GAP-08: Organization Extension
- **Current capability**: มี Module พื้นฐาน (UI/API) ขาด Field ย่อย.
- **Missing system work**: เพิ่มฟิลด์ใน UI `OrganizationManagementView.vue`, แก้ API `addOrganization` และ `updateOrganization`.
- **Missing configuration work**: Admin ข้อมูลลงระบบใหม่ตามฟิลด์ใหม่.
- **Frontend files**: `OrganizationManagementView.vue`
- **Backend files**: `organization_service.py`
- **Database changes**: Add columns (Type, Role, Contact, Owner, Source System relation) ลงใน `organization` table.
- **Migration**: ปล่อย NULL หรือ Default ให้ข้อมูลเก่า.
- **Backward compatibility**: Yes.
- **Dependencies**: -
- **Acceptance criteria**: เพิ่ม Organization พร้อมระบุ Role ได้.
- **Testing**: Unit (API save), Browser (Form input).
- **Estimate**: S
- **Deployment risk**: Low

### GAP-09: Label / Help Text
- **Current capability**: มี Label เดิมแต่กำกวม.
- **Missing system work**: อัปเดต Copywriting, เพิ่ม Placeholder และ Tooltip ℹ️.
- **Missing configuration work**: -
- **Frontend files**: ทุกไฟล์ใน `frontend/src/views/` ที่เกี่ยวข้อง.
- **Backend files**: -
- **Database changes**: -
- **Migration**: -
- **Backward compatibility**: Yes.
- **Dependencies**: -
- **Acceptance criteria**: ข้อความสื่อสารตรงกับคู่มือระบบ L2E.
- **Testing**: Browser (Visual validation).
- **Estimate**: S
- **Deployment risk**: Very Low

### GAP-10: Backend Master Data Validation
- **Current capability**: รับค่า text id ทุกอย่างโดยไม่ตรวจสอบ FK.
- **Missing system work**: เพิ่ม IF statement วิ่งหา Master Table ภายในฟังก์ชัน `addService` ก่อน `INSERT`.
- **Missing configuration work**: -
- **Frontend files**: -
- **Backend files**: `bigdataservice.py`
- **Database changes**: (Optional) เพิ่ม Foreign Key Constraint แท้จริงใน MySQL.
- **Migration**: (Optional) คลีนอัพ Data ขยะก่อนตั้ง Constraint.
- **Backward compatibility**: อาจทำ API 400 พังถ้าระบบเก่าส่งข้อมูลปลอมประจำ.
- **Dependencies**: -
- **Acceptance criteria**: ไม่สามารถ Save category หรือ organization ID ที่ไม่มีอยู่ใน Master Table ได้.
- **Testing**: Unit (API reject tests).
- **Estimate**: S
- **Deployment risk**: Medium

### GAP-11: UI/Functional Bugs
- **Current capability**: ใช้งานได้แต่มีบัคเรื้อรัง เช่น Double Scrollbar, Favorites ไม่รีเฟรช.
- **Missing system work**: ซ่อม Logic การเรียก API ซ้ำหลัง Add, แก้ CSS Overflow.
- **Missing configuration work**: -
- **Frontend files**: `AppSidebar.vue`, `DashboardView.vue`, `CatalogView.vue`
- **Backend files**: -
- **Database changes**: -
- **Migration**: -
- **Backward compatibility**: Yes.
- **Dependencies**: -
- **Acceptance criteria**: สกอร์ลบาร์ไม่ซ้อนกันสองชั้นในหน้า API Monitor และกดลบ Favorite แล้วหน้าจอตอบสนองทันที.
- **Testing**: Browser (Multi-viewport).
- **Estimate**: S
- **Deployment risk**: Low
