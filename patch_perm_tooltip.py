filepath = "frontend/src/views/PermissionManagementView.vue"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace :title with :data-tooltip and add class
content = content.replace(
    '<h4 :title="getMenuTooltip(perm.menu_name)" style="display: flex; align-items: center; gap: 6px; cursor: help;">',
    '<h4 :data-tooltip="getMenuTooltip(perm.menu_name)" class="custom-tooltip" style="display: flex; align-items: center; gap: 6px; cursor: help;">'
)

# And if I didn't add the css to PermissionManagementView yet:
css_addition = """
.custom-tooltip {
  position: relative;
}
.custom-tooltip::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: 100%;
  left: 0;
  transform: translateY(-5px);
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
  transform: translateY(0);
}
"""
if '.custom-tooltip' not in content:
    content = content.replace("</style>", css_addition + "\n</style>")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched PermissionManagementView tooltips")
