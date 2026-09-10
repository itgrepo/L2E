with open('frontend/src/views/APIManagementView.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the form row for API Type
form_row_to_remove = """            <div class="form-row">
              <label>API Type <span class="required">*</span></label>
              <select v-model="apiForm.api_type">
                <option value="general">general</option>
                <option value="scope">scope</option>
              </select>
            </div>"""
content = content.replace(form_row_to_remove, '')

with open('frontend/src/views/APIManagementView.vue', 'w', encoding='utf-8') as f:
    f.write(content)

