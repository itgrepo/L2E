import re

file_path = "frontend/src/components/AppNavbar.vue"
with open(file_path, "r") as f:
    content = f.read()

# Make toggleMobileMenu dispatch a global event
toggle_find = """const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};"""
toggle_repl = """const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
  window.dispatchEvent(new CustomEvent('toggle-mobile-menu', { detail: isMobileMenuOpen.value }));
};"""
content = content.replace(toggle_find, toggle_repl)

# Also close mobile menu should dispatch event
close_find = """const closeMobileMenu = () => {
  isMobileMenuOpen.value = false;
};"""
close_repl = """const closeMobileMenu = () => {
  isMobileMenuOpen.value = false;
  window.dispatchEvent(new CustomEvent('toggle-mobile-menu', { detail: false }));
};"""
content = content.replace(close_find, close_repl)

# Remove .mobile-side-tab
side_tab_find = """    <!-- Sticky Side Tab for Mobile -->
    <button class="mobile-side-tab" @click="toggleMobileMenu" aria-label="Open menu">
      <div class="tab-indicator"></div>
    </button>"""
content = content.replace(side_tab_find, "")

# Ensure responsive logo isn't overflowing
nav_css_find = """@media (max-width: 768px) {"""
nav_css_repl = """@media (max-width: 767px) {"""
content = content.replace(nav_css_find, nav_css_repl)

nav_css_inner_find = """.logo-text {
    font-size: 1rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 150px;
  }"""
nav_css_inner_repl = """.logo-text {
    font-size: 1rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 180px;
  }
  .nav-inner {
    padding-left: 16px;
    padding-right: 16px;
    justify-content: space-between;
  }
  .mobile-menu-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 8px;
    margin-right: -8px;
  }
"""
content = content.replace(nav_css_inner_find, nav_css_inner_repl)

with open(file_path, "w") as f:
    f.write(content)
print("Patched AppNavbar.vue")
