import sys

file_path = "frontend/src/views/CatalogView.vue"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """                    <div class="row"><span class="label">ชุดข้อมูลที่มีคุณค่าสูง</span><span class="value">{{ selectedDataset?.is_high_value || '-' }}</span></div>
                    <div class="row"><span class="label">ข้อมูลอ้างอิง</span><span class="value">{{ selectedDataset?.is_reference || '-' }}</span></div>
                    <div class="row"><span class="label">ความถี่การปรับปรุง</span><span class="value">{{ selectedDataset?.update_freq }}</span></div>
                    <div class="row"><span class="label">ขอบเขตข้อมูล</span><span class="value">{{ selectedDataset?.geo_scope }}</span></div>
                    
                    <div class="row-group-title">เทคนิคและติดต่อ</div>"""

replacement = """                    <div class="row"><span class="label">ชุดข้อมูลที่มีคุณค่าสูง</span><span class="value">{{ selectedDataset?.is_high_value || '-' }}</span></div>
                    <div class="row"><span class="label">ข้อมูลอ้างอิง</span><span class="value">{{ selectedDataset?.is_reference || '-' }}</span></div>
                    <div class="row" v-if="!['statistic', 'geospatial'].includes(selectedDataset?.dataset_type)"><span class="label">ความถี่การปรับปรุง</span><span class="value">{{ selectedDataset?.update_freq }}</span></div>
                    <div class="row" v-if="!['statistic', 'geospatial'].includes(selectedDataset?.dataset_type)"><span class="label">ขอบเขตข้อมูล</span><span class="value">{{ selectedDataset?.geo_scope }}</span></div>

                    <!-- STATISTIC SPECIFIC -->
                    <template v-if="selectedDataset?.dataset_type === 'statistic'">
                      <div class="row-group-title text-sky-600 border-sky-200 mt-4">ข้อมูลเฉพาะสถิติ</div>
                      <div class="row"><span class="label">ปีข้อมูลที่เริ่มจัดทำ</span><span class="value">{{ selectedDataset.stat_year_start || '-' }}</span></div>
                      <div class="row"><span class="label">ปีข้อมูลล่าสุด</span><span class="value">{{ selectedDataset.stat_year_latest || '-' }}</span></div>
                      <div class="row"><span class="label">การจัดจำแนก</span><span class="value">{{ selectedDataset.stat_classification || '-' }}</span></div>
                      <div class="row"><span class="label">หน่วยวัด</span><span class="value">{{ selectedDataset.stat_unit || '-' }}</span></div>
                      <div class="row"><span class="label">หน่วยตัวคูณ</span><span class="value">{{ selectedDataset.stat_multiplier || '-' }}</span></div>
                      <div class="row"><span class="label">วิธีการคำนวณ</span><span class="value">{{ selectedDataset.stat_calculation_method || '-' }}</span></div>
                      <div class="row"><span class="label">มาตรฐานการจัดทำข้อมูล</span><span class="value">{{ selectedDataset.stat_standard || '-' }}</span></div>
                      <div class="row"><span class="label">สถิติทางการ</span><span class="value">{{ selectedDataset.stat_official || '-' }}</span></div>
                    </template>

                    <!-- GEOSPATIAL SPECIFIC -->
                    <template v-if="selectedDataset?.dataset_type === 'geospatial'">
                      <div class="row-group-title text-emerald-600 border-emerald-200 mt-4">ข้อมูลภูมิสารสนเทศเชิงพื้นที่</div>
                      <div class="row"><span class="label">ชื่อชุดข้อมูลภูมิศาสตร์</span><span class="value">{{ selectedDataset.geo_dataset_name || '-' }}</span></div>
                      <div class="row"><span class="label">มาตราส่วน</span><span class="value">{{ selectedDataset.geo_scale || '-' }}</span></div>
                      <div class="row"><span class="label">ขอบเขต (W, E, N, S)</span><span class="value font-mono">{{ selectedDataset.geo_west_bound || '-' }}, {{ selectedDataset.geo_east_bound || '-' }}, {{ selectedDataset.geo_north_bound || '-' }}, {{ selectedDataset.geo_south_bound || '-' }}</span></div>
                      <div class="row"><span class="label">ความถูกต้องของตำแหน่ง</span><span class="value">{{ selectedDataset.geo_position_accuracy || '-' }}</span></div>
                      <div class="row"><span class="label">เวลาอ้างอิง</span><span class="value">{{ selectedDataset.geo_reference_time || '-' }}</span></div>
                      <div class="row"><span class="label">วันที่เผยแพร่ข้อมูล</span><span class="value">{{ selectedDataset.geo_published_date || '-' }}</span></div>
                    </template>
                    
                    <div class="row-group-title mt-4">เทคนิคและติดต่อ</div>"""

if target in content:
    content = content.replace(target, replacement)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Catalog updated successfully.")
else:
    print("Could not find target strings.")
