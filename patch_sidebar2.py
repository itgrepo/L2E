import re

file_path = "frontend/src/components/AppSidebar.vue"
with open(file_path, "r") as f:
    content = f.read()

# Remove the floating action button
fab_find = """    <!-- Floating Action Button for Mobile -->
    <button class="mobile-sidebar-toggle" @click="isMobileMenuOpen = !isMobileMenuOpen">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
      </svg>
    </button>"""
content = content.replace(fab_find, "")

# Add event listener in script setup
setup_find = """const isMobileMenuOpen = ref(false);"""
setup_repl = """const isMobileMenuOpen = ref(false);

onMounted(() => {
  window.addEventListener('toggle-sidebar', () => {
    isMobileMenuOpen.value = !isMobileMenuOpen.value;
  });
});"""
if "'toggle-sidebar'" not in content:
    content = content.replace(setup_find, setup_repl)

# Inject Global links inside the sidebar bottom
links_find = """      <button class="logout-btn" title="Logout" @click="handleLogout">
        <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        <span class="btn-text">ออกจากระบบ</span>
      </button>
    </div>
  </div>
</template>"""

links_repl = """      <button class="logout-btn" title="Logout" @click="handleLogout">
        <svg xmlns="http://www.w3.org/2000/svg" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        <span class="btn-text">ออกจากระบบ</span>
      </button>
      
      <!-- Global Links for Mobile Drawer -->
      <div class="global-mobile-links">
        <div class="divider"></div>
        <router-link to="/" class="global-link">หน้าแรก</router-link>
        <router-link to="/catalog" class="global-link">บัญชีข้อมูล</router-link>
        <router-link to="/analytics" class="global-link">วิเคราะห์</router-link>
        <router-link to="/about" class="global-link">เกี่ยวกับเรา</router-link>
      </div>
    </div>
  </div>
</template>"""
if "global-mobile-links" not in content:
    content = content.replace(links_find, links_repl)

# Update CSS for Breakpoint and Drawer behavior
css_find = """@media (max-width: 1024px) {"""
css_repl = """
.global-mobile-links {
  display: none;
}
@media (max-width: 767px) {
  .global-mobile-links {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 16px;
  }
  .global-link {
    color: #e2e8f0;
    text-decoration: none;
    font-size: 0.95rem;
    padding: 8px 12px;
    border-radius: 8px;
  }
  .divider {
    height: 1px;
    background: rgba(255,255,255,0.1);
    margin: 8px 0;
  }
"""
content = content.replace(css_find, css_repl + """@media (max-width: 767px) {""")

css_drawer_find = """  .app-sidebar {
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
  }"""

css_drawer_repl = """  .app-sidebar {
    position: fixed !important;
    top: 0;
    left: 0 !important;
    transform: translateX(-100%);
    width: 280px !important;
    max-width: 85vw !important;
    height: 100vh !important;
    z-index: 2000 !important;
    transition: transform 0.3s ease !important;
    box-shadow: none !important;
  }
  .app-sidebar.is-open {
    transform: translateX(0);
    box-shadow: 5px 0 25px rgba(0,0,0,0.5) !important;
  }"""
content = content.replace(css_drawer_find, css_drawer_repl)

# Update the media query closing
min1025_find = """@media (min-width: 1025px) {"""
min1025_repl = """@media (min-width: 768px) {"""
content = content.replace(min1025_find, min1025_repl)

with open(file_path, "w") as f:
    f.write(content)
print("Patched AppSidebar.vue")
