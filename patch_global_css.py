import re

file_path = "frontend/src/style.css"
with open(file_path, "r") as f:
    content = f.read()

responsive_css = """
/* Mobile Responsive Global Overrides */
@media (max-width: 768px) {
  .layout {
    flex-direction: column !important;
    width: 100% !important;
    max-width: 100vw !important;
    min-width: 0 !important;
    overflow-x: hidden !important;
  }
  
  .content {
    padding: 16px !important;
    width: 100% !important;
    max-width: 100vw !important;
    min-width: 0 !important;
    margin-left: 0 !important;
    box-sizing: border-box !important;
  }

  .page-header {
    flex-direction: column !important;
    align-items: flex-start !important;
    gap: 12px !important;
  }

  .page-header h1 {
    font-size: 1.5rem !important;
  }
  
  .table-card {
    padding: 16px !important;
    border-radius: 8px !important;
    width: 100% !important;
    min-width: 0 !important;
    overflow: hidden !important;
  }
  
  .table-header {
    flex-direction: column !important;
    align-items: stretch !important;
    gap: 16px !important;
  }

  .header-main {
    flex-direction: column !important;
    align-items: flex-start !important;
    gap: 12px !important;
    width: 100% !important;
  }

  .btn-add, .btn-save, .btn-primary {
    width: 100% !important;
    justify-content: center !important;
    min-height: 44px !important;
  }

  .search-bar, .search-bar input {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
  }

  /* Modals */
  .modal {
    width: calc(100vw - 32px) !important;
    max-width: 100% !important;
    max-height: calc(100dvh - 32px) !important;
    margin: 16px !important;
    display: flex !important;
    flex-direction: column !important;
  }
  
  .modal-body {
    overflow-y: auto !important;
    flex: 1 !important;
    padding: 16px !important;
  }
  
  .modal-footer {
    padding: 16px !important;
    flex-direction: column-reverse !important;
    gap: 12px !important;
  }
  
  .modal-footer button {
    width: 100% !important;
    min-height: 44px !important;
  }
  
  /* Footer */
  .site-footer {
    width: 100% !important;
    max-width: 100vw !important;
    padding: 24px 16px !important;
    box-sizing: border-box !important;
  }
  .footer-content {
    flex-direction: column !important;
    gap: 24px !important;
  }
  .footer-col {
    width: 100% !important;
    max-width: 100% !important;
  }
}
"""

if "Mobile Responsive Global Overrides" not in content:
    with open(file_path, "a") as f:
        f.write("\n" + responsive_css)
    print("Added mobile CSS to style.css")
else:
    print("CSS already exists")

