# L2E_WAVE0_COMMIT_MANIFEST

## 1. Description
This manifest defines the safe baseline for Wave 1 implementation, after Secret-risk remediation.

## 2. Include (Stage and Commit)

### Source Code
- `frontend/package-lock.json`
- `frontend/package.json`
- `frontend/src/App.vue`
- `frontend/src/components/AppNavbar.vue`
- `frontend/src/components/AppSidebar.vue`
- `frontend/src/views/UserManagementView.vue`

### Documentation
- `docs/gap-analysis/L2E_SYSTEM_GAPS_CURRENT_STATE_AUDIT.md`
- `docs/gap-analysis/L2E_SYSTEM_GAPS_IMPLEMENTATION_PLAN.md`
- `docs/gap-analysis/L2E_WAVE0_BASELINE_INVENTORY.md`
- `docs/gap-analysis/L2E_WAVE0_COMMIT_MANIFEST.md`
- `docs/responsive-audit/`
- `docs/security/L2E_CREDENTIAL_ROTATION_CHECKLIST.md`

### Deployment and Configuration
- `deploy_backend_frontend_hotfix.sh` (Sanitized)
- `deploy_backend_hotfix.sh` (Sanitized)
- `deploy_frontend_hotfix.sh` (Sanitized)
- `deploy_to_129.sh` (Sanitized)
- `deploy_to_3001.sh` (Sanitized)
- `deploy_to_3003.sh` (Sanitized)
- `Intelligist_install.sh` (Sanitized)
- `init_db_uat.sh` (Sanitized)
- `.gitignore` (Updated to protect secrets)
- `frontend/.env.test.example`

## 3. Exclude (DO NOT Stage or Commit)

### Quarantined / Deleted / Local Only
- `ubuntuL2E.key` (Moved to ~/.ssh/)
- `frontend/test_login.py` (Quarantined to /tmp)
- `frontend/test_db.cjs` (Quarantined to /tmp)
- `frontend/test_add_user*.cjs` (Quarantined to /tmp)
- `frontend/screenshot_add_user.cjs` (Quarantined to /tmp)
- `frontend/check_scroll.cjs` (Quarantined to /tmp)
- `frontend/find_overflow.cjs` (Quarantined to /tmp)
- `frontend/test_decode.py` (Quarantined to /tmp)
- `frontend/responsive_test.spec.js` (Quarantined to /tmp)
- `db_schema*.txt` (Quarantined to /tmp)
- `check_db.sql` (Quarantined to /tmp)
- `frontend/test-results/`

## 4. Verification
- Unresolved Secrets: 0
- Private Keys in working tree: 0
- Hardcoded passwords in scripts: 0
