import re

file_path = "frontend/src/components/AppSidebar.vue"
with open(file_path, "r") as f:
    content = f.read()

# Make sure Sidebar behaves as a Drawer on mobile
sidebar_css_find = """@media (max-width: 1024px) {"""
sidebar_css_repl = """@media (max-width: 1024px) {
  .app-sidebar {
    position: fixed !important;
    top: 0;
    left: -100% !important;
    width: 280px !important;
    max-width: 85vw !important;
    height: 100vh !important;
    z-index: 2000 !important;
    transition: left 0.3s ease !important;
  }
  .app-sidebar.is-open {
    left: 0 !important;
  }
"""

if "max-width: 85vw !important;" not in content:
    content = content.replace(sidebar_css_find, sidebar_css_repl)
    with open(file_path, "w") as f:
        f.write(content)
    print("Patched AppSidebar CSS")
else:
    print("AppSidebar already patched")
