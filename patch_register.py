import re

def main():
    filepath = "frontend/src/views/RegisterView.vue"
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add text for password rules
    content = content.replace(
        '<div class="password-strength" v-if="password">',
        '<div style="font-size: 0.8rem; color: #64748b; margin-top: 4px; margin-bottom: 8px;">* ต้องมีความยาวอย่างน้อย 8 ตัวอักษร, ประกอบด้วยตัวพิมพ์เล็ก, ตัวพิมพ์ใหญ่, ตัวเลข, และอักขระพิเศษ</div>\n              <div class="password-strength" v-if="password">'
    )

    # Change isStep1Valid logic
    isStep1Valid_new = """const isStep1Valid = computed(() => {
  return username.value.length >= 3 && 
         password.value.length >= 8 &&
         /[A-Z]/.test(password.value) &&
         /[a-z]/.test(password.value) &&
         /[0-9]/.test(password.value) &&
         /[^A-Za-z0-9]/.test(password.value) &&
         password.value === confirmPassword.value;
});"""
    content = re.sub(
        r"const isStep1Valid = computed\(\(\) => \{[\s\S]*?password\.value === confirmPassword\.value;\n\}\);",
        isStep1Valid_new,
        content
    )
    
    # Also update in template if it checks manually
    # Looking for `:disabled="... !password || password.length < 8 ..."`
    # There is no such hardcoded logic in the 'Next' button, it just uses `!isStep1Valid`

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched RegisterView.vue")

if __name__ == "__main__":
    main()
