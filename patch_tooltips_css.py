import re

def add_css_tooltip(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    css_addition = """
.custom-tooltip {
  position: relative;
}
.custom-tooltip::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%) translateY(-5px);
  background: rgba(0, 0, 0, 0.85);
  color: white;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  pointer-events: none;
  z-index: 999;
}
.custom-tooltip::before {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%) translateY(5px);
  border-width: 5px;
  border-style: solid;
  border-color: rgba(0, 0, 0, 0.85) transparent transparent transparent;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  pointer-events: none;
  z-index: 999;
}
.custom-tooltip:hover::after,
.custom-tooltip:hover::before {
  opacity: 1;
  visibility: visible;
  transform: translateX(-50%) translateY(0);
}
"""
    if '.custom-tooltip' not in content:
        content = content.replace("</style>", css_addition + "\n</style>")

    # replace title= with data-tooltip= and add class custom-tooltip
    content = content.replace('title="เพิ่ม/ลบ ชุดข้อมูลนี้ในรายการโปรดของคุณ"', 'data-tooltip="เพิ่ม/ลบ ในรายการโปรด" class="btn-favorite custom-tooltip"')
    content = content.replace('class="btn-favorite" :class="{ \'is-active\': isFavorite(ds) }" @click.stop.prevent="toggleFavorite(ds)" data-tooltip="เพิ่ม/ลบ ในรายการโปรด" class="btn-favorite custom-tooltip"', 'class="btn-favorite custom-tooltip" :class="{ \'is-active\': isFavorite(ds) }" @click.stop.prevent="toggleFavorite(ds)" data-tooltip="เพิ่ม/ลบ ในรายการโปรด"')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

add_css_tooltip("frontend/src/views/CatalogView.vue")

# For DashboardView.vue
with open("frontend/src/views/DashboardView.vue", 'r', encoding='utf-8') as f:
    content = f.read()

css_addition = """
.custom-tooltip {
  position: relative;
}
.custom-tooltip::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%) translateY(-5px);
  background: rgba(0, 0, 0, 0.85);
  color: white;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  pointer-events: none;
  z-index: 999;
}
.custom-tooltip:hover::after {
  opacity: 1;
  visibility: visible;
  transform: translateX(-50%) translateY(0);
}
"""
if '.custom-tooltip' not in content:
    content = content.replace("</style>", css_addition + "\n</style>")

content = content.replace(':title="`แสดงจำนวน ${stat.label} ทั้งหมด`"', ':data-tooltip="`จำนวน ${stat.label} ทั้งหมดในระบบ`" class="stat-card custom-tooltip"')
# Fix duplicate class if any
content = content.replace('class="stat-card" :data-tooltip', ':data-tooltip')

content = content.replace(':title="day.date + \': \' + day.count"', ':data-tooltip="day.date + \': \' + day.count" class="bar-track custom-tooltip"')
content = content.replace('class="bar-track" :data-tooltip', ':data-tooltip')

with open("frontend/src/views/DashboardView.vue", 'w', encoding='utf-8') as f:
    f.write(content)
print("Tooltips patched")
