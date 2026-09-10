with open('frontend/src/views/APIManagementView.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace generalApiServices and scopeApiServices with apiServices
old_computed = """const generalApiServices = computed(() => {
  return services.value.filter(s => s.api_endpoint && s.api_endpoint.trim() !== '' && (!s.api_type || s.api_type === 'general'));
});

const scopeApiServices = computed(() => {
  return services.value.filter(s => s.api_endpoint && s.api_endpoint.trim() !== '' && s.api_type === 'scope');
});"""

new_computed = """const apiServices = computed(() => {
  return services.value.filter(s => s.api_endpoint && s.api_endpoint.trim() !== '');
});"""

content = content.replace(old_computed, new_computed)

# Replace the v-for in the tabs
content = content.replace('<tr v-for="svc in generalApiServices"', '<tr v-for="svc in apiServices"')
content = content.replace('<tr v-for="svc in scopeApiServices"', '<tr v-for="svc in apiServices"')

with open('frontend/src/views/APIManagementView.vue', 'w', encoding='utf-8') as f:
    f.write(content)
