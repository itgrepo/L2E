# L2E_WAVE0_BASELINE_INVENTORY

## 1. Baseline Context
- **Original Branch**: `fix/l2e-full-responsive-uat`
- **Original Commit**: `d587d08b83d7d0cce1dbfb37f50f4c914b3b1ad1`
- **New Safety Branch**: `feature/l2e-wave1-security-validation`

## 2. Modified & Untracked Files Classification

### SOURCE
- `frontend/package-lock.json`
- `frontend/package.json`
- `frontend/src/App.vue`
- `frontend/src/components/AppNavbar.vue`
- `frontend/src/components/AppSidebar.vue`
- `frontend/src/views/UserManagementView.vue`

### TEST
- `frontend/test_add_user.cjs`
- `frontend/test_add_user_payload.cjs`
- `frontend/test_add_user_real.cjs`
- `frontend/test_add_user_submit.cjs`
- `frontend/test_add_user_submit2.cjs`
- `frontend/test_db.cjs`
- `frontend/test_decode.py`
- `frontend/test_login.py`
- `frontend/responsive_test.spec.js`
- `frontend/screenshot_add_user.cjs`

### DOCUMENTATION
- `docs/gap-analysis/L2E_SYSTEM_GAPS_CURRENT_STATE_AUDIT.md`
- `docs/gap-analysis/L2E_SYSTEM_GAPS_IMPLEMENTATION_PLAN.md`
- `docs/responsive-audit/*` (Images and folders)

### MIGRATION
- (None)

### DEPLOYMENT_SCRIPT
- `deploy_backend_frontend_hotfix.sh`
- `deploy_backend_hotfix.sh`
- `deploy_frontend_hotfix.sh`

### GENERATED
- `db_schema.txt`
- `db_schema2.txt`
- `db_schema3.txt`
- `check_db.sql`
- `frontend/test-results/.last-run.json`

### SECRET_RISK
- `frontend/test_login.py` (Potential hardcoded test credentials/passwords)
- `frontend/test_db.cjs` (Potential DB connection strings/passwords)
- `frontend/test_add_user_real.cjs` (Potential login credentials)

### UNRELATED
- `frontend/check_scroll.cjs`
- `frontend/find_overflow.cjs`

## 3. Include Manifest for Wave 0 Commit
To safely commit the baseline without exposing secrets or generated noise, only the following categories should be staged:
- SOURCE
- DOCUMENTATION

The following categories must NOT be included in the commit, or should be cleaned/added to `.gitignore`:
- GENERATED
- SECRET_RISK (Unless sanitized)
- UNRELATED
- TEST (Temporary ad-hoc test scripts)
- DEPLOYMENT_SCRIPT (Unless verified and intended for source control)
