import re

with open('frontend/src/views/DatasetConfigView.vue', 'r', encoding='utf-8') as f:
    content = f.read()

computed_code = """
const showGovConflict = computed(() => {
  return (formData.value.access_type === 'pii' || formData.value.access_type === 'restricted' || formData.value.access_type === 'internal') && formData.value.gov_category === 'ข้อมูลสาธารณะ';
});
"""

# Insert after the formData object ends
content = re.sub(
    r'(external_api_url: \'\'\n\}\);)',
    r'\1\n' + computed_code,
    content
)

with open('frontend/src/views/DatasetConfigView.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patched DatasetConfigView.vue")
