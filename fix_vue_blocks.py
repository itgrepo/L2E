import sys

file_path = "frontend/src/views/DatasetConfigView.vue"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Inject Sub-Navbar for Dataset Type
target_1 = """            <form @submit.prevent="handleSubmit" class="config-form">
              <!-- Section 1: Basic Information -->"""

replacement_1 = """            <form @submit.prevent="handleSubmit" class="config-form">
              <div class="dataset-type-selector mt-4 mb-6">
                <label class="block text-slate-700 font-semibold mb-2" style="font-size: 1.1rem; border-bottom: 2px solid #0f766e; padding-bottom: 0.5rem; display: inline-block;">ประเภทชุดข้อมูล (Dataset Type) *</label>
                <div class="flex flex-wrap gap-2 mt-2" style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem;">
                  <button 
                    type="button"
                    v-for="type in [
                      { id: 'record', name: 'ข้อมูลระเบียน' },
                      { id: 'statistic', name: 'ข้อมูลสถิติ' },
                      { id: 'geospatial', name: 'ข้อมูลภูมิสารสนเทศเชิงพื้นที่' },
                      { id: 'various', name: 'ข้อมูลหลากหลายประเภท' },
                      { id: 'other', name: 'ข้อมูลประเภทอื่นๆ' }
                    ]" 
                    :key="type.id"
                    @click="formData.dataset_type = type.id"
                    style="padding: 0.5rem 1rem; border-radius: 0.375rem; border: 1px solid #cbd5e1; font-size: 0.875rem; font-weight: 500; cursor: pointer; transition: all 0.2s;"
                    :style="formData.dataset_type === type.id ? 'background-color: #0f766e; color: white; border-color: #0f766e;' : 'background-color: white; color: #475569;'"
                  >
                    {{ type.name }}
                  </button>
                </div>
              </div>

              <!-- Section 1: Basic Information -->"""

if target_1 in content:
    content = content.replace(target_1, replacement_1)

# 2. Wrap original specific fields and add new ones
target_2_start = """                <div class="form-row">
                  <div class="form-group">
                    <label>ความถี่ที่เกี่ยวกับข้อมูล *</label>"""

target_2_end = """              <!-- Section 3: Contact & Additional Tech -->"""

# Extract the middle block
start_idx = content.find(target_2_start)
end_idx = content.find(target_2_end)

if start_idx != -1 and end_idx != -1:
    original_specific = content[start_idx:end_idx]
    
    new_specific = f"""              <!-- DYNAMIC SECTION: RECORD / VARIOUS / OTHER -->
              <div v-if="['record', 'various', 'other'].includes(formData.dataset_type)">
{original_specific}              </div>

              <!-- DYNAMIC SECTION: STATISTIC -->
              <div v-if="formData.dataset_type === 'statistic'" class="form-section-block mt-8" style="border-left: 4px solid #0ea5e9; padding-left: 1rem;">
                <h3 class="block-title text-sky-600">ข้อมูลเฉพาะ: ข้อมูลสถิติ</h3>
                <div class="form-row">
                  <div class="form-group">
                    <label>ปีข้อมูลที่เริ่มต้นจัดทำ *</label>
                    <input type="text" v-model="formData.stat_year_start" class="form-input-custom" placeholder="เช่น 2560" required>
                  </div>
                  <div class="form-group">
                    <label>ปีข้อมูลล่าสุดที่เผยแพร่ *</label>
                    <input type="text" v-model="formData.stat_year_latest" class="form-input-custom" placeholder="เช่น 2566" required>
                  </div>
                </div>
                <div class="form-group">
                  <label>การจัดจำแนก *</label>
                  <input type="text" v-model="formData.stat_classification" class="form-input-custom" placeholder="ระบุการจัดจำแนก" required>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>หน่วยวัด *</label>
                    <input type="text" v-model="formData.stat_unit" class="form-input-custom" placeholder="เช่น คน, บาท, ราย" required>
                  </div>
                  <div class="form-group">
                    <label>หน่วยตัวคูณ *</label>
                    <input type="text" v-model="formData.stat_multiplier" class="form-input-custom" placeholder="เช่น พัน, ล้าน" required>
                  </div>
                </div>
                <div class="form-group">
                  <label>วิธีการคำนวณ *</label>
                  <textarea v-model="formData.stat_calculation_method" rows="2" placeholder="อธิบายสูตรหรือวิธีการคำนวณ..." required></textarea>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>มาตรฐานการจัดทำข้อมูล *</label>
                    <input type="text" v-model="formData.stat_standard" class="form-input-custom" placeholder="ระบุมาตรฐานที่ใช้อ้างอิง" required>
                  </div>
                  <div class="form-group">
                    <label>สถิติทางการ *</label>
                    <select v-model="formData.stat_official" class="form-select-custom" required>
                      <option>ใช่</option>
                      <option>ไม่ใช่</option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- DYNAMIC SECTION: GEOSPATIAL -->
              <div v-if="formData.dataset_type === 'geospatial'" class="form-section-block mt-8" style="border-left: 4px solid #10b981; padding-left: 1rem;">
                <h3 class="block-title text-emerald-600">ข้อมูลเฉพาะ: ข้อมูลภูมิสารสนเทศเชิงพื้นที่</h3>
                <div class="form-row">
                  <div class="form-group">
                    <label>ชุดข้อมูลภูมิศาสตร์ *</label>
                    <input type="text" v-model="formData.geo_dataset_name" class="form-input-custom" placeholder="ชื่อชุดข้อมูลภูมิศาสตร์" required>
                  </div>
                  <div class="form-group">
                    <label>มาตราส่วน *</label>
                    <input type="text" v-model="formData.geo_scale" class="form-input-custom" placeholder="เช่น 1:50000" required>
                  </div>
                </div>
                
                <h4 class="font-semibold text-slate-700 mb-2 mt-4" style="font-size: 0.95rem;">กรอบพื้นที่ (Bounding Box) *</h4>
                <div class="form-row" style="background: #f8fafc; padding: 1rem; border-radius: 0.5rem; border: 1px solid #e2e8f0; margin-bottom: 1rem;">
                  <div class="form-group">
                    <label>ทิศตะวันตก (West)</label>
                    <input type="text" v-model="formData.geo_west_bound" class="form-input-custom" placeholder="Longitude" required>
                  </div>
                  <div class="form-group">
                    <label>ทิศตะวันออก (East)</label>
                    <input type="text" v-model="formData.geo_east_bound" class="form-input-custom" placeholder="Longitude" required>
                  </div>
                  <div class="form-group">
                    <label>ทิศเหนือ (North)</label>
                    <input type="text" v-model="formData.geo_north_bound" class="form-input-custom" placeholder="Latitude" required>
                  </div>
                  <div class="form-group">
                    <label>ทิศใต้ (South)</label>
                    <input type="text" v-model="formData.geo_south_bound" class="form-input-custom" placeholder="Latitude" required>
                  </div>
                </div>

                <div class="form-group">
                  <label>ความถูกต้องของตำแหน่ง *</label>
                  <input type="text" v-model="formData.geo_position_accuracy" class="form-input-custom" placeholder="ระบุความคลาดเคลื่อน (ถ้ามี)" required>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>เวลาอ้างอิง *</label>
                    <input type="text" v-model="formData.geo_reference_time" class="form-input-custom" placeholder="ระบุเวลาอ้างอิงของข้อมูลพิกัด" required>
                  </div>
                  <div class="form-group">
                    <label>วันที่เผยแพร่ข้อมูล *</label>
                    <input type="date" v-model="formData.geo_published_date" class="form-input-custom" required>
                  </div>
                </div>
              </div>

              <!-- Section 3: Contact & Additional Tech -->"""
    
    content = content[:start_idx] + new_specific + content[end_idx + len(target_2_end):]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Frontend form refactored successfully.")
else:
    print("Could not find boundaries for extraction.")

