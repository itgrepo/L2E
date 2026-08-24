import os

file_paths = [
    "frontend/src/views/CatalogView.vue",
    "frontend/src/views/DatasetManagementView.vue"
]

for file_path in file_paths:
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
        
        # Look for flex-wrap: wrap in mobile css
        find_css = """  .search-input-wrapper {
    flex-wrap: wrap;
    gap: 8px;
    padding: 8px;
  }"""
        repl_css = """  .search-input-wrapper {
    flex-direction: column;
    gap: 8px;
    padding: 8px;
    background: transparent;
    border: none;
    box-shadow: none;
  }
  .search-input-wrapper input {
    width: 100%;
    background-color: white !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 12px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
  }
  .search-input-wrapper .btn-search,
  .search-input-wrapper .btn-add-dataset {
    width: 100%;
    margin: 0;
  }
  .search-input-wrapper > * {
    width: 100%;
  }
"""
        content = content.replace(find_css, repl_css)
        with open(file_path, "w") as f:
            f.write(content)
        print(f"Patched {file_path}")
