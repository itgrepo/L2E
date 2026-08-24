import re

file_path = "frontend/src/components/AppNavbar.vue"
with open(file_path, "r") as f:
    content = f.read()

# Add a specific media query for small mobile devices
navbar_css_find = """@media (max-width: 768px) {"""
navbar_css_repl = """@media (max-width: 768px) {
  .nav-inner {
    padding-left: 12px;
    padding-right: 12px;
  }
  .logo-text {
    font-size: 1rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 150px;
  }
"""

if "max-width: 150px;" not in content:
    content = content.replace(navbar_css_find, navbar_css_repl)
    with open(file_path, "w") as f:
        f.write(content)
    print("Patched AppNavbar CSS")
else:
    print("AppNavbar already patched")
