with open('frontend/src/views/APIManagementView.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace apiServices computed property
old_computed = """const apiServices = computed(() => {
  return services.value.filter(s => s.api_endpoint && s.api_endpoint.trim() !== '');
});"""

new_computed = """const generalApiServices = computed(() => {
  return services.value.filter(s => s.api_endpoint && s.api_endpoint.trim() !== '' && (!s.api_type || s.api_type === 'general'));
});

const scopeApiServices = computed(() => {
  return services.value.filter(s => s.api_endpoint && s.api_endpoint.trim() !== '' && s.api_type === 'scope');
});"""

content = content.replace(old_computed, new_computed)

# Replace the v-for in the tabs
# First find the activeTab === 'general' block
# It should be around line 631, we can replace the first instance
content = content.replace('<tr v-for="svc in apiServices"', '<tr v-for="svc in generalApiServices"', 1)
# Then replace the second instance (which is in the 'scopes' tab)
content = content.replace('<tr v-for="svc in apiServices"', '<tr v-for="svc in scopeApiServices"', 1)

with open('frontend/src/views/APIManagementView.vue', 'w', encoding='utf-8') as f:
    f.write(content)
