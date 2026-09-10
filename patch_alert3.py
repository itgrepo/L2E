filepath = "frontend/src/views/DatasetManagementView.vue"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

old_css = """.alert-banner {
  padding: 12px 20px;
  border-radius: 12px;
  margin-bottom: 24px;
  font-weight: 600;
  font-size: 0.875rem;
}"""

new_css = """.alert-banner {
  padding: 12px 20px;
  border-radius: 12px;
  margin-bottom: 24px;
  font-weight: 600;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.alert-close-btn {
    background: transparent;
    border: none;
    color: inherit;
    font-size: 1.5rem;
    line-height: 1;
    cursor: pointer;
    opacity: 0.6;
    padding: 0;
    margin: -4px -8px -4px 0;
    transition: opacity 0.2s;
}
.alert-close-btn:hover {
    opacity: 1;
}"""

content = content.replace(old_css, new_css)
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
