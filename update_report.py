path = "/Users/natthawutjantakul/.gemini/antigravity/brain/922529c0-c12e-4424-b378-50d7bfb37fa2/e2e_final_report.md"
with open(path, "r") as f:
    content = f.read()

old_section = "## 6. Account Lifecycle E2E Test (Zero-State to Password Reset)"
new_section = """## 6. Account Lifecycle E2E Test (Real SMTP Delivery)

**Test Target:** `afourdy2134@gmail.com`
**Environment:** `134.185.172.127:3003` (Configured to use Real SMTP `outgoing.workd.go.th:465`)

| Step | Action | Endpoint | Result | Notes |
|------|--------|----------|--------|-------|
| 1 | Register Account | `/registerSimple` | ✅ PASS | Created successfully. Triggered Verification Email. |
| 2 | Verification Email Delivery | N/A | ⚠️ BLOCKED | - Trigger: PASS<br>- SMTP Submission: PASS<br>- Real Gmail Delivery: BLOCKED (Agent cannot access Gmail Inbox)<br>- Content Verification: BLOCKED |
| 3 | Verify Token | `/verify/<TOKEN>` | ✅ PASS | DB `status_id` updated to `1` (Active). (Note: Token extracted from DB to continue flow). |
| 4 | First Login | `/login` | ✅ PASS | Successful login. Account Verified = TRUE. |
| 5 | Forgot Password | `/forgotPassword` | ✅ PASS | Request accepted. Triggered Password Reset Email. |
| 6 | Reset Email Delivery | N/A | ⚠️ BLOCKED | - Trigger: PASS<br>- SMTP Submission: PASS<br>- Real Gmail Delivery: BLOCKED<br>- Content Verification: BLOCKED |
| 7 | Reset Password | `/resetPasswordByToken` | ✅ PASS | Successfully changed the password. |
| 8 | Login with OLD PW | `/login` | ✅ PASS | Old password was REJECTED. |
| 9 | Login with NEW PW | `/login` | ✅ PASS | New password was ACCEPTED. |

> [!NOTE]
> **Real Delivery Verification Blocked**
> The Backend successfully generated and submitted the emails to the Real SMTP Server (`outgoing.workd.go.th`). The SMTP Server accepted the relay request without throwing `Access denied` after we patched the authentication. However, since the AI Agent cannot physically open the `afourdy2134@gmail.com` Inbox to verify content, those specific checks are marked as BLOCKED according to QA guidelines.

> [!WARNING]
> **Missing Functionality: Password Changed Notification**
> Tested the system for a security notification triggered after a successful password reset.
> **Result:** `NO PASSWORD-CHANGED NOTIFICATION IMPLEMENTED`

"""

if old_section in content:
    content = content.split(old_section)[0] + new_section
else:
    content += "\n---\n\n" + new_section

with open(path, "w") as f:
    f.write(content)
print("Updated report!")
