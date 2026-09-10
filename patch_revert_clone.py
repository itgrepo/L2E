with open('frontend/src/views/APIManagementView.vue', 'r', encoding='utf-8') as f:
    content = f.read()

old_code = """      user: encodeUserData(userData),
      service_id: apiForm.value.report_id,"""

new_code = """      user: encodeUserData(userData),
      original_service_id: apiForm.value.report_id,"""

content = content.replace(old_code, new_code)

old_code2 = """    };
    const res = await apiClient.post('/saveApiConfig', payload);"""

new_code2 = """    };
    const res = await apiClient.post('/cloneServiceForApi', payload);"""

content = content.replace(old_code2, new_code2)

with open('frontend/src/views/APIManagementView.vue', 'w', encoding='utf-8') as f:
    f.write(content)
