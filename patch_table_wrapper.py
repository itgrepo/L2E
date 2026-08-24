import re

file_path = "frontend/src/style.css"
with open(file_path, "r") as f:
    content = f.read()

# Make sure tables don't cause root overflow
fix_css = """
  /* Generic Table Mobile Fix */
  .table-container, .table-responsive, .data-table-wrapper {
    width: 100% !important;
    max-width: 100vw !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch;
  }
  
  table, .data-table {
    min-width: 600px; /* Let it scroll inside the wrapper */
  }
"""

if "Generic Table Mobile Fix" not in content:
    # insert before the closing brace of the @media (max-width: 768px)
    content = content.replace("}\n\"\"\"", fix_css + "}\n\"\"\"") # Wait, my python script before appended it to the file
    content = content.replace("  .footer-col {\n    width: 100% !important;\n    max-width: 100% !important;\n  }\n}", "  .footer-col {\n    width: 100% !important;\n    max-width: 100% !important;\n  }\n" + fix_css + "}")
    
    with open(file_path, "w") as f:
        f.write(content)
    print("Patched table wrappers")
