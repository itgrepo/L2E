# L2E API Management — Final Runtime Validation & Security Remediation Plan

> **Audit Date**: 2026-07-29  
> **Auditor**: Antigravity Agent  
> **Scope**: Static code analysis of Working Tree  
> **Constraint**: No code changes, no commits, no DB changes, no deploy

---

## 1. Baseline Record

### Git State

| Item | Value |
|------|-------|
| Branch | `main` |
| HEAD Commit | `72e86d04de280e7314b159305009287afd95e48b` |
| Modified Tracked Files | 38 files |
| Deleted Tracked Files | 1 (`walkthrough.md`) |
| Untracked Files | ~130+ files |

### Key API Management Files — Source Classification

| File | Classification | Notes |
|------|---------------|-------|
| `backendold/Astro_backend/app/ServiceConfig/bigdataservice.py` | **Modified tracked** | Core API Management backend — all Control Plane + Data Plane endpoints |
| `backendold/Astro_backend/app/ServiceConfig/__init__.py` | **Modified tracked** | Contains `checkUserIsAdmin()`, `logAction()`, DB config |
| `backendold/Astro_backend/app/ServiceConfig/notification_util.py` | **Untracked** | `notify_user()` / `notify_all_users()` |
| `frontend/src/views/APIManagementView.vue` | **Modified tracked** | Full Control Plane UI |
| `frontend/src/views/ApiMonitorView.vue` | **Modified tracked** | Monitor/Logs UI |

> [!CAUTION]
> The entire API Management system exists **only in the Working Tree** (uncommitted modifications + untracked files). The Final Result **cannot be reproduced from commit hash `72e86d04` alone**. A commit capturing the current Working Tree state is required before any deployment can be considered reproducible.

---

## 2. Static Audit Finding Validation

### Finding F1: Broken Access Control

**Static Audit Claim**: "User ธรรมดาทุกคนสามารถเข้าถึงฟังก์ชันระดับแอดมินทั้งหมดได้"

**Validation**: **CONFIRMED_STATIC**

The codebase contains **two distinct broken auth patterns**:

**Pattern A** (used in newer API Management endpoints):
```python
# bigdataservice.py lines 992, 1149, 1184, 1206, 1285, 1581, 1620, 1663
if not user_data.get("user_id") and not checkUserIsAdmin(user_data):
    return jsonify({"status": "Permission Denied"})
```
**Why broken**: When `user_data` has a `user_id` (any logged-in user), `not user_data.get("user_id")` evaluates to `False`. Since Python uses short-circuit evaluation on `and`, the entire condition becomes `False` regardless of `checkUserIsAdmin`. The guard **never fires for any authenticated user**.

**Pattern B** (used in older service endpoints):
```python
# bigdataservice.py lines 49, 362, 402, 436
if user_data.get('user_id') or checkUserIsAdmin(user_data):
    # proceed with admin action
```
**Why broken**: Any user with a `user_id` (any logged-in user) satisfies the `or`, so the admin check is never evaluated. **Same net effect**.

**Pattern C** (no auth at all):
```python
# bigdataservice.py line 945 — /getApiCredentials
# No user parameter check whatsoever
```

**Impact Breakdown**:
- **Unauthenticated users**: The `platform_decode(dataInput['user'])` call will raise a `KeyError` or `json.JSONDecodeError` if `user` is missing/invalid, which falls to the `except` block returning an error. So unauthenticated access is **blocked by accident** (via exception), not by design.
- **Authenticated non-admin users**: **Full access to all Control Plane operations**. They can create/delete credentials, modify scopes, change API configs, view all secrets.

### Finding F2: Secret Key Stored as Plaintext

**Validation**: **CONFIRMED_STATIC**

Evidence from [bigdataservice.py](file:///Users/natthawutjantakul/intelligist_dataX/backendold/Astro_backend/app/ServiceConfig/bigdataservice.py#L1019):
```python
# Line 1019-1023: INSERT with plaintext secret_key
sql_insert = "INSERT INTO api_credentials (service_id, user_id, secret_key, status, expires_at) VALUES (%s, %s, %s, 'active', %s)"
cursor.execute(sql_insert, (service_id, target_user_id, secret_key, expires_at))
```

DB schema confirmation from `intelligist_datax_full_dump.sql`:
```sql
`secret_key` varchar(64) NOT NULL,
```
Actual dump data shows plaintext hex strings:
```
'c2ede410f3df62e5e8ca8030de23fd27'
```

### Finding F3: Secret Readable via API

**Validation**: **CONFIRMED_STATIC**

- `/getApiCredentials` (line 954) does `SELECT c.secret_key` and returns it in JSON. **No auth check at all**.
- `/getAllApiScopes` (line 1586) also `SELECT c.secret_key` and returns it.
- `/addApiCredential` (line 1035) returns `secret_key` in the creation response.
- Frontend (line 483) displays secret with a toggle eye icon, meaning the full plaintext is in the browser's JavaScript memory.

### Finding F4: API Key via Query String

**Validation**: **CONFIRMED_STATIC**

Evidence from [bigdataservice.py](file:///Users/natthawutjantakul/intelligist_dataX/backendold/Astro_backend/app/ServiceConfig/bigdataservice.py#L564):
```python
apikey = request.args.get('apikey')  # Line 564 — query string only
```
No `request.headers.get('x-api-key')` or `Authorization` header parsing exists anywhere.

### Finding F5: Error Information Leakage

**Validation**: **CONFIRMED_STATIC — str(e), NOT full stack trace**

The Data Plane returns `str(e)` which is the exception message, not a full stack trace:
```python
# Line 798
return jsonify({'status': 'error', 'message': str(e)}), 500
```

Additionally, several Control Plane endpoints expose **line numbers**:
```python
# Lines 1037-1039
exception_type, exception_object, exception_traceback = sys.exc_info()
line_number = exception_traceback.tb_lineno
return jsonify({"status": "Error: " + str(e), "Line number": line_number})
```

This is `str(e)` + line number, which can reveal table names, column names, and SQL errors. **Not a full Python traceback**, but still information leakage.

---

## 3. Authorization Matrix

| # | Endpoint | Line | Auth Pattern | Unauthenticated | Auth Non-Admin | Admin | Expected |
|---|----------|------|-------------|-----------------|----------------|-------|----------|
| 1 | `/addService` | 49 | Pattern B | Blocked (exception) | **ALLOWED** | Allowed | Admin only |
| 2 | `/getService` | 362 | Pattern B | Blocked (exception) | **ALLOWED** | Allowed | Admin only |
| 3 | `/getServiceCredential` | 402 | Pattern B | Blocked (exception) | **ALLOWED** | Allowed | Admin only |
| 4 | `/addServiceCredential` | 436 | Pattern B | Blocked (exception) | **ALLOWED** | Allowed | Admin only |
| 5 | `/retrieveService` | 500 | None (public) | Allowed | Allowed | Allowed | OK (catalog) |
| 6 | `/dataapi/api/v1/<id>` | 554 | API Key check | Blocked (401) | Via API Key | Via API Key | OK |
| 7 | `/getAvailableDatabases` | 810 | Pattern A | Blocked (exception) | **ALLOWED** | Allowed | Admin only |
| 8 | `/getAvailableTables` | 823 | Pattern A | Blocked (exception) | **ALLOWED** | Allowed | Admin only |
| 9 | `/getTableColumns` | 856 | Pattern A | Blocked (exception) | **ALLOWED** | Allowed | Admin only |
| 10 | `/saveApiConfig` | 887 | Pattern A | Blocked (exception) | **ALLOWED** | Allowed | Admin only |
| 11 | `/getApiCredentials` | 945 | **NONE** | **ALLOWED** | **ALLOWED** | Allowed | Admin only |
| 12 | `/addApiCredential` | 985 | Pattern A | Blocked (exception) | **ALLOWED** | Allowed | Admin only |
| 13 | `/extendApiCredential` | 1041 | Pattern A | Blocked (exception) | **ALLOWED** | Allowed | Admin only |
| 14 | `/revokeApiCredential` | 1070 | Pattern A | Blocked (exception) | **ALLOWED** | Allowed | Admin only |
| 15 | `/resumeApiCredential` | 1092 | Pattern A | Blocked (exception) | **ALLOWED** | Allowed | Admin only |
| 16 | `/deleteApiCredential` | 1114 | Pattern A | Blocked (exception) | **ALLOWED** | Allowed | Admin only |
| 17 | `/updateApiScope` | 1142 | Pattern A | Blocked (exception) | **ALLOWED** | Allowed | Admin only |
| 18 | `/getAvailableUsers` | 1177 | Pattern A | Blocked (exception) | **ALLOWED** | Allowed | Admin only |
| 19 | `/getApiMonitorStats` | 1200 | Pattern A | Blocked (exception) | **ALLOWED** | Allowed | Admin only |
| 20 | `/getApiMonitorLogs` | 1279 | Pattern A | Blocked (exception) | **ALLOWED** | Allowed | Admin only |
| 21 | `/getAllApiScopes` | 1575 | Pattern A | Blocked (exception) | **ALLOWED** | Allowed | Admin only |
| 22 | `/saveApiScopeForUser` | 1614 | Pattern A | Blocked (exception) | **ALLOWED** | Allowed | Admin only |
| 23 | `/deleteApiScopeForUser` | 1657 | Pattern A | Blocked (exception) | **ALLOWED** | Allowed | Admin only |

**Summary**: 21 out of 23 endpoints have broken or missing authorization. `/getApiCredentials` is the worst — completely open with no auth check, returning all secrets.

### Proposed Centralized Fix

```python
# Decorator-based approach
def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        dataInput = request.json or request.form
        user_str = dataInput.get('user')
        if not user_str:
            return jsonify({"status": "error", "message": "Authentication required"}), 401
        try:
            user_data = json.loads(platform_decode(user_str))
        except:
            return jsonify({"status": "error", "message": "Invalid user data"}), 401
        if not checkUserIsAdmin(user_data):
            return jsonify({"status": "error", "message": "Admin access required"}), 403
        request.current_user = user_data
        return f(*args, **kwargs)
    return decorated
```

Apply to every endpoint: `@require_admin` decorator replaces all inline checks. This must be applied to **all 21 affected endpoints**, not just a few.

---

## 4. Credential Security Design

### Current Flow

| Step | Current Behavior | Risk |
|------|-----------------|------|
| Secret Generation | Backend: `uuid.uuid4().hex` (line 1003) | Acceptable entropy but `uuid4` is not CSPRNG on all platforms |
| Client-Supplied Secret | **Yes** — `dataInput.get('secret_key', '')` (line 997) | Allows weak/predictable keys |
| Storage | **Plaintext** in `api_credentials.secret_key` | DB breach = full compromise |
| Lookup | `WHERE secret_key = %s AND service_id = %s` (line 626) | Plaintext comparison |
| Listing | `/getApiCredentials` returns full `secret_key` | Unlimited reads, no auth |
| Display | Frontend toggle show/hide per credential | All secrets in browser memory |
| Logging | `log_api_usage` logs status message, NOT apikey | OK |
| URL exposure | `?apikey=xxx` in query string | Browser history, proxy logs |

### Target Design

**Key Format**: `datax_<public_id>.<secret_part>`

Example: `datax_cred42.a8f3b1c2e5d7f9012345678901234567`

**Database Schema** (new columns for `api_credentials`):

| Column | Type | Description |
|--------|------|-------------|
| `credential_id` | INT PK | Auto-increment |
| `service_id` | INT FK | References service |
| `user_id` | INT FK | References user |
| `public_key_id` | VARCHAR(20) | Public prefix for lookup (e.g., `cred42`) |
| `secret_hash` | VARCHAR(128) | SHA-256 hash of full key |
| `key_last_four` | CHAR(4) | Last 4 chars for display |
| `status` | ENUM | `active`, `paused`, `revoked` |
| `expires_at` | DATETIME | Nullable |
| `revoked_at` | DATETIME | Set when revoked |
| `created_at` | TIMESTAMP | Default CURRENT_TIMESTAMP |
| `updated_at` | TIMESTAMP | On update |

**Lookup Strategy**:
1. Parse incoming key: split on `.` → `public_id` + `secret`
2. Query: `SELECT * FROM api_credentials WHERE public_key_id = %s`
3. Verify: `sha256(incoming_secret) == stored_secret_hash`
4. Single DB lookup (indexed on `public_key_id`), no full-table scan

**Lifecycle Semantics**:

| Action | Status Change | Key Reusable | Reversible |
|--------|--------------|-------------|------------|
| Create | → `active` | Yes (first display) | N/A |
| Pause | `active` → `paused` | Same key | Yes (Resume) |
| Resume | `paused` → `active` | Same key | Yes |
| Revoke | `active`/`paused` → `revoked`, set `revoked_at` | Key disabled permanently | **No** |
| Delete | Hard DELETE from DB + associated scopes | Key gone forever | No |

**Migration Plan for Existing Keys**:
1. Add new columns (`public_key_id`, `secret_hash`, `key_last_four`) to `api_credentials`
2. For each existing row: generate `public_key_id`, compute `sha256(secret_key)`, extract last 4 chars
3. Populate new columns
4. Deploy new code that reads from new columns
5. After verification period, drop `secret_key` column

---

## 5. API Key Transport

### Current: Query String `?apikey=<secret>`

**Exposure Points**:
- Browser history/bookmarks
- Reverse proxy access logs (nginx/apache default log format includes query string)
- Application-level URL logging
- Referrer header when navigating away
- Screenshots of browser URL bar
- Shared URLs via chat/email

### Target: `x-api-key` Header

**Recommendation**: Use `x-api-key: <API_KEY>` as the primary method.

Rationale over `Authorization: Bearer`:
- `x-api-key` is a dedicated API key header, semantically clearer
- `Authorization: Bearer` is typically reserved for OAuth2/JWT tokens
- Less risk of collision with future auth mechanisms

### Migration Plan

| Phase | Duration | Behavior |
|-------|----------|----------|
| Phase 1: Dual Support | Weeks 1-4 | Accept both `x-api-key` header AND `?apikey` query param. If query param is used, add deprecation warning in response header `X-Deprecation-Warning: Query string API keys are deprecated. Use x-api-key header.` |
| Phase 2: Warning + Log | Weeks 5-8 | Same dual support, but log all query-string usage as `DEPRECATED` in access log |
| Phase 3: Cutoff | Week 9+ | Remove query string support. Return 400 error if `?apikey` is detected |

**Implementation**:
```python
apikey = request.headers.get('x-api-key') or request.args.get('apikey')
deprecated_transport = bool(request.args.get('apikey'))
# add deprecation warning to response if deprecated_transport
```

**Tests Required**:
- Header-only request works
- Query-string-only request works during Phase 1-2
- No key returns 401
- Key in both header and query string: header takes precedence

---

## 6. Data Plane Runtime Test Design

| # | Test Case | Preconditions | Request | Expected HTTP | Expected Response | Actual/Status |
|---|-----------|--------------|---------|---------------|-------------------|---------------|
| 1 | No API Key | Active API, type != public | `GET /dataapi/api/v1/DS001` | 401 | `Missing apikey parameter` | BLOCKED (no live server) |
| 2 | Invalid API Key | Active API | `GET /dataapi/api/v1/DS001?apikey=invalid` | 403 | `Invalid or inactive API key` | BLOCKED |
| 3 | Valid Active Key | Active API + active credential | `GET /dataapi/api/v1/DS001?apikey=valid` | 200 | JSON with `rows` array | BLOCKED |
| 4 | Key for Wrong Service | Key belongs to service_id=2 | `GET /dataapi/api/v1/DS001?apikey=wrongservice` | 403 | `Invalid or inactive API key` | BLOCKED |
| 5 | Paused (Revoked) Credential | Credential status = 'revoked' | `GET /dataapi/api/v1/DS001?apikey=paused` | 403 | `API Key is inactive` | BLOCKED |
| 6 | Resumed Credential | Status changed back to 'active' | Same key | 200 | Data returned | BLOCKED |
| 7 | Revoked Credential | Status = 'revoked' | Same key | 403 | `API Key is inactive` | BLOCKED |
| 8 | Deleted Credential | Row deleted from DB | Same key | 403 | `Invalid or inactive API key` | BLOCKED |
| 9 | Expired Credential | `expires_at < now()` | Same key | 403 | `API Key has expired` | BLOCKED |
| 10 | Extended Credential | `expires_at` pushed to future | Same key | 200 | Data returned | BLOCKED |
| 11 | Disabled API | `api_enabled = 0` | Any valid key | 403 | `API access is disabled` | BLOCKED |
| 12 | Re-enabled API | `api_enabled = 1` | Same key | 200 | Data returned | BLOCKED |
| 13 | Permission after re-enable | Credentials untouched | Same key | 200 | Same data | BLOCKED |
| 14 | Allowed Request Field | `?field_name=value` where field in req_fields | 200 | Filtered results | BLOCKED |
| 15 | Unknown Request Field | `?unknown_field=value` | 200 | Field ignored (no filter) | BLOCKED |
| 16 | Response Field Filtering | `api_response_fields = ["col1","col2"]` | 200 | Only col1, col2 in rows | BLOCKED |
| 17 | Scope = operator | `scope_json: [{field:"x", operator:"=", value:"1"}]` | 200 | Only rows where x=1 | BLOCKED |
| 18 | Scope IN operator | `operator: "IN", value: ["a","b"]` | 200 | Only matching rows | BLOCKED |
| 19 | Scope LIKE operator | `operator: "LIKE", value: "%test%"` | 200 | Pattern-matched rows | BLOCKED |
| 20 | Scope AND logic | Multiple conditions, logic: AND | 200 | Intersection of conditions | BLOCKED |
| 21 | Scope OR logic | Multiple conditions, logic: OR | 200 | Union of conditions | BLOCKED |
| 22 | Empty Scope | No scope record | 200 | All rows (up to LIMIT) | BLOCKED |
| 23 | Invalid Operator in scope_json | `operator: "DROP"` | 200 | Operator ignored, `1=1` | BLOCKED |
| 24 | Invalid Column in scope_json | `field: "nonexistent_col"` | 500 | Error (unknown column) | BLOCKED |
| 25 | SQL Injection in scope value | `value: "1; DROP TABLE user--"` | 200 | Parameterized, no injection | BLOCKED |
| 26 | Error response content | Force DB error | 500 | `str(e)` returned — INFO LEAK | BLOCKED |
| 27 | 1000 row limit | Table with >1000 rows | 200 | Max 1000 rows | BLOCKED |
| 28 | API Key not in access log | Check `log` table after call | N/A | `log_detail` has status only | BLOCKED |

**BLOCKED Reason**: All tests require a live running server with configured database. Cannot execute runtime tests in this audit round.

---

## 7. Dynamic SQL & Source Validation

### Identifier Analysis

| Identifier | Source | Validation | Used In SQL |
|-----------|--------|-----------|-------------|
| `db_name` | `service.api_db_name` (admin-configured) | Config-time: `ALLOWED_DATABASES` whitelist. Runtime: hardcoded list `['psu_backend', 'datalake', 'default', 'datax_db', 'datax_db_3001']` | f-string in `FROM \`{db_name}\`.\`{source_name}\`` |
| `source_name` | `service.api_source_name` (admin-configured) | **NONE** — no validation at config or runtime | f-string in `FROM \`{db_name}\`.\`{source_name}\`` |
| `res_fields` | `service.api_response_fields` (admin-configured) | **NONE** — values from JSON array used directly | f-string: `` \`{f}\` `` in SELECT clause |
| `req_fields` | `service.api_request_fields` (admin-configured) | **NONE** — values from JSON array used directly | f-string: `` \`{field}\` `` in WHERE clause |
| `scope.field` | `api_scopes.scope_json` (admin-configured) | Regex: `^[a-zA-Z0-9_]+$` | f-string: `` \`{field}\` `` in WHERE |
| `scope.value` | `api_scopes.scope_json` (admin-configured) | **None** but uses `%s` parameterized | Parameterized `%s` |

### Findings

1. **Whitelist Mismatch**: Config-time `ALLOWED_DATABASES` = `['psu_backend', 'datalake', 'default']` (line 808), but runtime whitelist = `['psu_backend', 'datalake', 'default', 'datax_db', 'datax_db_3001']` (line 749). Two extra databases at runtime.

2. **source_name Not Validated**: The table/view name is taken from the `service` table and injected into SQL wrapped only in backticks. Since this value is set by admin (who currently = any logged-in user due to broken auth), this is exploitable. Even with proper auth, backtick-only protection is insufficient — a value like `` `user` WHERE 1=1; -- `` could escape the backtick context.

3. **Response/Request Fields Not Validated**: Column names from `api_response_fields` and `api_request_fields` are used in SELECT and WHERE clauses with backtick wrapping only. No regex validation like scope fields have.

4. **Scope Fields ARE Validated**: `re.match(r'^[a-zA-Z0-9_]+$', field)` at line 714. Values use parameterized queries. This is the strongest protection in the codebase.

### Required Remediation

- Validate `source_name` with regex `^[a-zA-Z0-9_]+$` at both config-time and runtime
- Validate `res_fields` and `req_fields` column names with same regex
- Unify whitelist constants (single source of truth)
- Consider querying `INFORMATION_SCHEMA.TABLES` at runtime to verify table exists

---

## 8. Error Handling

### Current Behavior by Endpoint Type

| Context | Error Response | Line Numbers | Severity |
|---------|---------------|-------------|----------|
| Data Plane 500 | `{"status": "error", "message": str(e)}` | 798 | **Medium** — reveals SQL errors with table/column names |
| Data Plane log | `str(e)[:50]` truncated in log_detail | 792 | Low |
| Control Plane (new) | `{"status": "Error: " + str(e)}` | 1175, 1198 | Medium |
| Control Plane (old) | `{"status": "Error: " + str(e), "Line number": N}` | 389, 425, 495, 553, 1039 | **High** — reveals source file line numbers |

### Correction from Static Audit

The static audit stated "Full Stack Trace" — this is **REJECTED**. The actual behavior is `str(e)` (exception message only) plus optional line numbers. There is no `traceback.format_exc()` in any response. However, `exc_info=True` is passed to `current_app.logger.error()` (line 797), which logs the full stack trace to **server logs** (correct behavior).

### Target Design

```python
# All client-facing errors:
return jsonify({
    "status": "error",
    "message": "An internal error occurred",
    "request_id": request_id
}), 500

# Server log only:
current_app.logger.error(f"[{request_id}] {traceback.format_exc()}")
```

---

## 9. Audit & Access Logging

### Current State: Control Plane

| Event | `logAction` Called | Evidence |
|-------|--------------------|----------|
| Create API (`/addService`) | No | Line 43-350, no logAction call |
| Update API Config (`/saveApiConfig`) | No | Line 887-944, no logAction call |
| Enable/Disable API | No | Part of saveApiConfig |
| Create Credential (`/addApiCredential`) | No | Line 985-1039, no logAction call |
| Pause Credential (`/revokeApiCredential`) | No | Line 1070-1090, no logAction call |
| Resume Credential | No | Line 1092-1112, no logAction call |
| Extend Credential | No | Line 1041-1068, no logAction call |
| Delete Credential | No | Line 1114-1140, no logAction call |
| Update Scope | No | Line 1142-1175, no logAction call |
| Delete Scope | No | Line 1657-1675, no logAction call |

**Conclusion**: Zero audit logging for any Control Plane operation.

### Current State: Data Plane

| Event | Logged | Fields Captured |
|-------|--------|----------------|
| Successful API call | Yes | user_id, `[200] API Invoked Successfully`, path, IP |
| Failed: missing key | Yes | user_id=0, `[401] Missing apikey parameter`, path, IP |
| Failed: invalid key | Yes | user_id=0, `[403] Invalid API key`, path, IP |
| Failed: inactive key | Yes | user_id, `[403] API Key is inactive`, path, IP |
| Failed: expired | Yes | user_id, `[403] API Key has expired`, path, IP |
| Failed: no permission | Yes | user_id, `[403] Access Denied`, path, IP |
| Failed: API disabled | Yes | user_id=0, `[403] API access is disabled`, path, IP |
| Failed: internal error | Yes | user_id=0, `[500] System Error: {msg[:50]}`, path, IP |

**Missing from Data Plane logs**: service_id, credential_id, HTTP method, response time, request_id, user_agent, full status_code (embedded in text instead).

### Target: Control Plane Audit Log Schema

```sql
CREATE TABLE api_audit_log (
    audit_id        INT AUTO_INCREMENT PRIMARY KEY,
    actor_user_id   INT NOT NULL,
    target_user_id  INT DEFAULT NULL,
    service_id      INT DEFAULT NULL,
    credential_id   INT DEFAULT NULL,
    action          VARCHAR(50) NOT NULL,
    before_data     JSON DEFAULT NULL,
    after_data      JSON DEFAULT NULL,
    result          VARCHAR(20) NOT NULL DEFAULT 'success',
    ip_address      VARCHAR(45),
    user_agent      VARCHAR(500),
    request_id      VARCHAR(36),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_actor (actor_user_id),
    INDEX idx_service (service_id),
    INDEX idx_action (action),
    INDEX idx_created (created_at)
);
```

---

## 10. Final Status Matrix

| # | Capability | Static Status | Runtime Status | Security Status | Evidence | Required Work |
|---|-----------|--------------|---------------|----------------|----------|--------------|
| 1 | API Configuration (CRUD) | IMPLEMENTED_UNVERIFIED | BLOCKED | **BROKEN** (auth bypass) | `saveApiConfig` L887 | P0.1 Auth fix |
| 2 | DB/Table/Column Discovery | IMPLEMENTED_UNVERIFIED | BLOCKED | **BROKEN** (auth bypass) | `getAvailableDatabases` L810 | P0.1 Auth fix |
| 3 | Credential Create | IMPLEMENTED_UNVERIFIED | BLOCKED | **BROKEN** (auth bypass + plaintext + client-supplied key) | `addApiCredential` L985 | P0.1 + P0.2 |
| 4 | Credential List | IMPLEMENTED_UNVERIFIED | BLOCKED | **BROKEN** (NO auth + secret exposure) | `getApiCredentials` L945 | P0.1 + P0.2 |
| 5 | Credential Pause/Resume | IMPLEMENTED_UNVERIFIED | BLOCKED | **BROKEN** (auth bypass) | `revokeApiCredential` L1070 | P0.1 |
| 6 | Credential Extend | IMPLEMENTED_UNVERIFIED | BLOCKED | **BROKEN** (auth bypass) | `extendApiCredential` L1041 | P0.1 |
| 7 | Credential Delete | IMPLEMENTED_UNVERIFIED | BLOCKED | **BROKEN** (auth bypass) | `deleteApiCredential` L1114 | P0.1 |
| 8 | Scope Management | IMPLEMENTED_UNVERIFIED | BLOCKED | **BROKEN** (auth bypass) | `updateApiScope` L1142 | P0.1 |
| 9 | Data Plane Runtime | IMPLEMENTED_UNVERIFIED | BLOCKED | PARTIAL (key via query string, info leak) | `/dataapi/api/v1/<id>` L554 | P0.3 + P0.4 |
| 10 | API-Level Pause | IMPLEMENTED_UNVERIFIED | BLOCKED | OK (runtime enforced) | `api_enabled` check L603 | — |
| 11 | Credential-Level Pause | IMPLEMENTED_UNVERIFIED | BLOCKED | OK (runtime enforced) | `status != active` check L638 | — |
| 12 | Expiration | IMPLEMENTED_UNVERIFIED | BLOCKED | OK (runtime enforced) | `expires_at < now()` L644 | P1.4 (timezone) |
| 13 | Scope Enforcement | IMPLEMENTED_UNVERIFIED | BLOCKED | OK (parameterized + field regex) | Scope parsing L696-731 | — |
| 14 | Control Plane Audit Log | NOT_FOUND | NOT_FOUND | NOT_FOUND | Zero logAction calls | P1.1 |
| 15 | Data Plane Access Log | PARTIAL | BLOCKED | PARTIAL (missing fields) | `log_api_usage` L570 | P1.2 |
| 16 | Dynamic SQL Safety | PARTIAL | BLOCKED | **BROKEN** (source_name, field names unvalidated) | `final_sql` L757 | P0.5 |

---

## 11. Implementation Plan

### P0.1 Backend Authorization — Size: M

| Item | Detail |
|------|--------|
| **Current** | Two broken auth patterns (A: `not X and not Y`, B: `X or Y`) + one endpoint with zero auth |
| **Expected** | All Control Plane endpoints require admin. Return 401/403 with proper HTTP status codes |
| **Root Cause** | `if not user_data.get("user_id") and not checkUserIsAdmin(user_data):` — AND logic is inverted. Comment `# Loosen check for presentation` confirms intentional weakening |
| **Files** | `bigdataservice.py` (21 endpoints), possibly `group_service.py`, `register.py` |
| **DB Migration** | None |
| **Backward Compat** | Non-admin users who currently access these endpoints will lose access |
| **Acceptance Criteria** | (1) Unauthenticated → 401, (2) Non-admin → 403, (3) Admin → 200, for every CP endpoint |
| **Tests** | Unit: mock user payloads for each role × each endpoint. Integration: actual HTTP calls with test users |
| **Security Tests** | Attempt each endpoint without user param; with non-admin user; with admin user |
| **Dependencies** | None |
| **Estimate** | M (1-2 days) |
| **Deployment Risk** | Medium — existing non-admin users may rely on current behavior |
| **Rollback** | Revert decorator additions |

---

### P0.2 Credential Hashing & One-Time Secret — Size: L

| Item | Detail |
|------|--------|
| **Current** | Secret stored plaintext, returned on every list call, client can supply own secret |
| **Expected** | Secret generated server-side only, shown once at creation, stored as SHA-256 hash |
| **Root Cause** | `dataInput.get('secret_key', '')` accepts client value; `SELECT c.secret_key` returns plaintext |
| **Files** | `bigdataservice.py` (`addApiCredential`, `getApiCredentials`, `getAllApiScopes`, `saveApiScopeForUser`), `APIManagementView.vue` |
| **DB Migration** | ALTER TABLE `api_credentials` ADD `public_key_id`, `secret_hash`, `key_last_four`; data migration for existing rows; DROP `secret_key` after verification |
| **Backward Compat** | Breaking change — existing keys need one-time migration, Frontend must show "Created secret" dialog |
| **Acceptance Criteria** | (1) No plaintext secret in DB, (2) `/getApiCredentials` returns only `key_last_four`, (3) `/addApiCredential` returns secret once, (4) Data Plane uses hash lookup |
| **Tests** | Unit: hash verification, creation flow. Integration: create → list → verify secret not visible |
| **Dependencies** | P0.1 (auth must be fixed first) |
| **Estimate** | L (3-5 days) |
| **Deployment Risk** | High — existing integrations using current keys will break if not migrated |
| **Rollback** | Keep old `secret_key` column during transition, dual-read strategy |

---

### P0.3 Header-Based API Key & Query Key Deprecation — Size: S

| Item | Detail |
|------|--------|
| **Current** | `request.args.get('apikey')` only |
| **Expected** | `request.headers.get('x-api-key')` primary, query string deprecated |
| **Root Cause** | Original implementation used simplest approach |
| **Files** | `bigdataservice.py` line 564 |
| **DB Migration** | None |
| **Backward Compat** | Phase 1-2: dual support. Phase 3: query string removed |
| **Acceptance Criteria** | (1) `x-api-key` header works, (2) Query string works with deprecation warning, (3) No key → 401 |
| **Tests** | Header-only, query-only, both, neither |
| **Dependencies** | None |
| **Estimate** | S (< 1 day) |
| **Deployment Risk** | Low — additive change with backward compat |
| **Rollback** | Revert to query-only |

---

### P0.4 Error Sanitization — Size: S

| Item | Detail |
|------|--------|
| **Current** | `str(e)` + line numbers returned to client |
| **Expected** | Generic error message + request_id to client; full details in server log only |
| **Root Cause** | Debug-mode error handling left in production code |
| **Files** | `bigdataservice.py` — all `except` blocks (approximately 20+ locations) |
| **DB Migration** | None |
| **Backward Compat** | Clients relying on error messages for logic will need adjustment |
| **Acceptance Criteria** | No error response contains table names, column names, line numbers, or SQL fragments |
| **Tests** | Trigger errors (bad input, missing fields) and verify response is generic |
| **Dependencies** | None |
| **Estimate** | S (< 1 day) |
| **Deployment Risk** | Low |
| **Rollback** | Revert |

---

### P0.5 Dynamic SQL Identifier Validation — Size: M

| Item | Detail |
|------|--------|
| **Current** | `source_name` and field names used in SQL with backtick-only protection |
| **Expected** | All identifiers validated with regex `^[a-zA-Z0-9_]+$`; whitelist unified |
| **Root Cause** | Scope fields have validation, but other identifiers do not |
| **Files** | `bigdataservice.py` — `saveApiConfig` (config-time) and `get_dataset_api` (runtime) |
| **DB Migration** | None |
| **Backward Compat** | Existing configs with valid names unaffected |
| **Acceptance Criteria** | (1) Invalid identifier rejected at config-time, (2) Invalid identifier blocked at runtime, (3) Single `ALLOWED_DATABASES` constant |
| **Tests** | Config with special chars rejected; runtime with injected name blocked |
| **Dependencies** | None |
| **Estimate** | M (1-2 days) |
| **Deployment Risk** | Low |
| **Rollback** | Revert |

---

### P0.6 Security Regression Tests — Size: M

| Item | Detail |
|------|--------|
| **Current** | No automated security tests |
| **Expected** | Test suite covering auth bypass, secret exposure, SQL injection, error leakage |
| **Files** | New test file(s) |
| **Acceptance Criteria** | All P0 fixes verified by automated tests that fail if regression occurs |
| **Dependencies** | P0.1-P0.5 |
| **Estimate** | M (1-2 days) |

---

### P1.1 Control Plane Audit Log — Size: M

| Item | Detail |
|------|--------|
| **Current** | Zero audit logging for Control Plane operations |
| **Expected** | Every create/update/delete/status-change logged to `api_audit_log` table |
| **Files** | `bigdataservice.py` — all 12 operations listed in Section 9 |
| **DB Migration** | CREATE TABLE `api_audit_log` |
| **Estimate** | M (2-3 days) |

### P1.2 Access Log Enhancement — Size: S

Add `service_id`, `credential_id`, `status_code`, `duration_ms`, `request_id`, `user_agent` to Data Plane access log.

### P1.3 Credential Lifecycle Semantics — Size: S

Distinguish `paused` from `revoked` in DB enum. Currently both use `revoked` status with same column. Add `paused` to enum and `revoked_at` timestamp.

### P1.4 Timezone & Expiry Boundary — Size: S

Current: `datetime.now()` (server local time). Target: `datetime.utcnow()` or timezone-aware comparison. Define boundary: `expires_at <= now()` means expired (currently `<`).

### P1.5 Runtime E2E Test Suite — Size: L

Implement all 28 test cases from Section 6 as automated integration tests.

### P2 (Future)

- Notification before credential expiry
- Usage dashboard per credential
- Search/filter credentials and logs
- Key rotation UX (create new key, deprecate old)

---

## 12. Final Answers

| # | Question | Answer |
|---|----------|--------|
| 1 | ระบบสร้าง Dynamic Data API ได้จริงหรือไม่ | **Yes** — Config → DB mapping → runtime query path exists in code |
| 2 | Control Plane และ Data Plane เชื่อมกันจริงหรือไม่ | **Yes** — `saveApiConfig` writes to `service` table, Data Plane reads from same table via `dataset_id` |
| 3 | User ธรรมดาข้าม Admin Authorization ได้จริงหรือไม่ | **Yes — CONFIRMED_STATIC** — broken `and`/`or` logic in 21 of 23 endpoints |
| 4 | ผู้ใช้ที่ไม่ Login เข้าถึงได้หรือไม่ | **Partially** — `/getApiCredentials` has zero auth (any POST works). Other endpoints blocked by exception (not by design) |
| 5 | Secret ถูกเก็บ Plaintext จริงหรือไม่ | **Yes — CONFIRMED_STATIC** — `varchar(64)` with hex values visible in SQL dump |
| 6 | Secret ถูกอ่านกลับได้หรือไม่ | **Yes — CONFIRMED_STATIC** — `/getApiCredentials` returns `secret_key` field, no auth required |
| 7 | Key ผ่าน Query String มีจุดรั่วตรงไหนบ้าง | Browser history, proxy/web server access logs, Referrer header, URL sharing |
| 8 | Scope ถูก Apply จริงหรือไม่ | **Yes (code path confirmed)** — when `api_type == 'scope'`, scope_json is parsed and applied |
| 9 | Scope ผ่าน SQL Injection Test หรือไม่ | **BLOCKED** (no runtime test) — but code uses parameterized queries for values + regex for field names |
| 10 | API Pause/Resume ทำงานจริงหรือไม่ | **IMPLEMENTED_UNVERIFIED** — code path checks `api_enabled` and blocks when 0 |
| 11 | Credential Pause/Resume ทำงานจริงหรือไม่ | **IMPLEMENTED_UNVERIFIED** — code path checks `status == 'active'` |
| 12 | Expiry ทำงานจริงหรือไม่ | **IMPLEMENTED_UNVERIFIED** — code path checks `expires_at < datetime.now()` |
| 13 | งาน P0 ที่ต้องแก้ก่อนเปิดใช้งาน | P0.1 Auth, P0.2 Secret Hashing, P0.3 Key Transport, P0.4 Error Sanitization, P0.5 SQL Validation, P0.6 Security Tests |
| 14 | Product Decisions ที่ต้องยืนยัน | (1) Should existing keys be force-rotated or migrated? (2) Should `paused` vs `revoked` be separate states? (3) Should `/getApiCredentials` exist at all or only show masked view? (4) Is the `ALLOWED_DATABASES` whitelist correct? (5) Should non-admin users see the API Management menu at all? |

---

## Summary

- **Baseline**: Commit `72e86d04` + modified Working Tree (38 modified + 130+ untracked files)
- **Working Tree**: All API Management code is in **uncommitted state** — not reproducible from commit hash alone
- **Critical Findings Confirmed**: 3 P0 security issues (Broken Auth, Plaintext Secrets, No-Auth Secret Endpoint)
- **P0 Implementation Order**: P0.1 (Auth) → P0.3 (Key Transport) → P0.4 (Error Sanitization) → P0.5 (SQL Validation) → P0.2 (Secret Hashing) → P0.6 (Regression Tests)
- **Blockers**: No live server available for runtime validation — all test cases are BLOCKED
- **Final Report**: `docs/gap-analysis/L2E_API_MANAGEMENT_FINAL_REPORT.md`
