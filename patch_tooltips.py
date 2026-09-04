import re

# CatalogView.vue
with open("frontend/src/views/CatalogView.vue", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    '<button class="btn-favorite" :class="{ \'is-active\': isFavorite(ds) }" @click.stop.prevent="toggleFavorite(ds)">',
    '<button class="btn-favorite" :class="{ \'is-active\': isFavorite(ds) }" @click.stop.prevent="toggleFavorite(ds)" title="เพิ่ม/ลบ ชุดข้อมูลนี้ในรายการโปรดของคุณ">'
)
with open("frontend/src/views/CatalogView.vue", "w", encoding="utf-8") as f:
    f.write(content)

# DashboardView.vue
with open("frontend/src/views/DashboardView.vue", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    '<div v-for="stat in stats" :key="stat.label" class="stat-card">',
    '<div v-for="stat in stats" :key="stat.label" class="stat-card" :title="`แสดงจำนวน ${stat.label} ทั้งหมด`">'
)
with open("frontend/src/views/DashboardView.vue", "w", encoding="utf-8") as f:
    f.write(content)

print("Patched tooltips")
