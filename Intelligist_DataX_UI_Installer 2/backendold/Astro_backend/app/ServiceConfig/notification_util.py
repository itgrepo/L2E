from ServiceConfig import mysql
import logging

logger = logging.getLogger(__name__)

def notify_user(user_id, notif_type, message):
    if not user_id:
        return
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notifications (user_id, type, message) VALUES (%s, %s, %s)", (user_id, notif_type, message))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Failed to send notification:", e)

def notify_all_users(notif_type, message):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM user WHERE status_account = 'active'")
        users = cursor.fetchall()
        for u in users:
            cursor.execute("INSERT INTO notifications (user_id, type, message) VALUES (%s, %s, %s)", (u[0], notif_type, message))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Failed to notify all users:", e)

def notify_dataset_lifecycle(service_id, event_type='updated', custom_message=None):
    """
    หลักการการแจ้งเตือน L2E (In-App และ Email) เมื่อมีการสร้างหรือแก้ไขชุดข้อมูล:
    1. จำกัดสิทธิ์ (Restricted):
       - เมื่อสร้าง (created): แจ้งเตือนทุกคน
       - เมื่ออัปเดต (updated): ไม่ควรมีการแจ้งเตือน (ไม่มีใครได้รับแจ้งเตือน)
    2. ภายในหน่วยงาน (Internal):
       - เมื่อสร้าง (created): แจ้งเตือนคนในหน่วยงานนั้นเท่านั้น
       - เมื่อแก้ไข (updated): แจ้งเตือนคนในหน่วยงานนั้นเท่านั้น
    3. สาธารณะ (Public):
       - เมื่อสร้าง (created): แจ้งเตือนทุกคน
       - เมื่อแก้ไข (updated): แจ้งแค่คนที่กด Favorite ชุดข้อมูลนั้นเท่านั้น (ถ้าไม่ได้กดใจไม่ต้องแจ้งเตือน)
    4. เฉพาะเจ้าของ (Private/PII):
       - เมื่อสร้าง (created): แจ้งเตือนแค่คนที่สร้าง
       - เมื่อแก้ไข (updated): แจ้งเตือนแค่คนที่สร้าง
    """
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        # Fetch dataset details
        cursor.execute("""
            SELECT service_name, access_type, organization, l2e_group_id, created_by, contact_email, description 
            FROM service WHERE service_id = %s
        """, (service_id,))
        svc = cursor.fetchone()
        if not svc:
            cursor.close()
            conn.close()
            return set()

        service_name, access_type, org_name, l2e_group_id, created_by, contact_email, svc_desc = svc
        access_type_lower = str(access_type or 'public').lower().strip()
        svc_title = service_name or f"ID {service_id}"

        recipients = set()

        is_restricted = ('restricted' in access_type_lower) or ('จำกัดสิทธิ์' in access_type_lower)
        is_internal = ('internal' in access_type_lower) or ('ภายในหน่วยงาน' in access_type_lower)
        is_public = ('public' in access_type_lower) or ('สาธารณะ' in access_type_lower)
        is_private = ('private' in access_type_lower) or ('pii' in access_type_lower) or ('เฉพาะเจ้าของ' in access_type_lower)

        # 1. จำกัดสิทธิ์ (Restricted)
        if is_restricted:
            if event_type == 'created':
                cursor.execute("SELECT user_id FROM user WHERE status_account = 'active'")
                recipients = {row[0] for row in cursor.fetchall() if row[0]}
            else:
                # อัปเดต Restricted: ไม่ควรมีการแจ้งเตือน (ไม่มีใครได้รับแจ้งเตือน)
                recipients = set()

        # 2. ภายในหน่วยงาน (Internal)
        elif is_internal:
            if org_name and str(org_name).strip():
                clean_org = str(org_name).strip()
                cursor.execute("""
                    SELECT u.user_id FROM user u 
                    LEFT JOIN organization o ON u.org_id = o.org_id 
                    WHERE (TRIM(o.org_name) = TRIM(%s) OR CAST(u.org_id AS CHAR) = TRIM(%s)) 
                      AND u.status_account = 'active'
                """, (clean_org, clean_org))
                recipients = {row[0] for row in cursor.fetchall() if row[0]}
            else:
                recipients = set()

        # 3. สาธารณะ (Public)
        elif is_public:
            if event_type == 'created':
                cursor.execute("SELECT user_id FROM user WHERE status_account = 'active'")
                recipients = {row[0] for row in cursor.fetchall() if row[0]}
            else:
                # แก้ไข Public: แจ้งแค่คนที่กด Favorite ชุดข้อมูลนั้นเท่านั้น
                cursor.execute("""
                    SELECT DISTINCT uf.user_id 
                    FROM user_favorites uf
                    JOIN user u ON uf.user_id = u.user_id 
                    WHERE uf.service_id = %s AND u.status_account = 'active'
                """, (service_id,))
                recipients = {row[0] for row in cursor.fetchall() if row[0]}

        # 4. เฉพาะเจ้าของ (Private / PII)
        elif is_private:
            if created_by:
                cursor.execute("SELECT user_id FROM user WHERE user_id = %s AND status_account = 'active'", (created_by,))
                c_row = cursor.fetchone()
                if c_row and c_row[0]:
                    recipients.add(c_row[0])
            elif contact_email:
                cursor.execute("SELECT user_id FROM user WHERE LOWER(email) = LOWER(%s) AND status_account = 'active'", (contact_email.strip(),))
                c_row = cursor.fetchone()
                if c_row and c_row[0]:
                    recipients.add(c_row[0])

        if not recipients:
            cursor.close()
            conn.close()
            return set()

        # Prepare in-app message
        if custom_message:
            message = custom_message
        elif event_type == 'created':
            message = f'มีชุดข้อมูลใหม่เข้าสู่ระบบ: "{svc_title}"'
        else:
            message = f'ชุดข้อมูล "{svc_title}" มีการอัปเดตข้อมูลใหม่'

        notif_type = f'dataset_{event_type}'
        for uid in recipients:
            cursor.execute("INSERT INTO notifications (user_id, type, message) VALUES (%s, %s, %s)", (uid, notif_type, message))

        # Send Email notification to the same recipients
        try:
            format_strings = ','.join(['%s'] * len(recipients))
            cursor.execute(f"SELECT email FROM user WHERE user_id IN ({format_strings}) AND email IS NOT NULL AND status_account = 'active'", tuple(recipients))
            recipient_emails = [row[0] for row in cursor.fetchall() if row[0]]
            if recipient_emails:
                if event_type == 'created':
                    from .email_service import notify_dataset_created
                    notify_dataset_created(svc_title, svc_desc or '', recipient_emails)
                else:
                    from .email_service import notify_dataset_updated
                    notify_dataset_updated(svc_title, recipient_emails)
        except Exception as mail_err:
            logger.warning(f"Could not send email notifications: {mail_err}")

        conn.commit()
        cursor.close()
        conn.close()
        return recipients
    except Exception as e:
        print("Failed to notify dataset lifecycle:", e)
        return set()

def notify_dataset_interest(service_id, notif_type, message):
    """Backward compatibility wrapper: routes to notify_dataset_lifecycle."""
    event_type = 'created' if 'สร้าง' in str(message) or notif_type == 'dataset_created' else 'updated'
    notify_dataset_lifecycle(service_id, event_type, custom_message=message)

def notify_dataset_access(service_id, access_method='download', actor_user_id=None, detail=''):
    """
    หลักการการแจ้งเตือนกระดิ่ง L2E เมื่อมีการเข้าถึงชุดข้อมูล:
    *** ไม่ว่าการแจ้งเตือนใด "คนสร้างชุดข้อมูล" ที่เป็นเจ้าของ จะต้องได้รับการแจ้งเตือนทุกกรณี
        และทุกการเข้าถึงเมื่อมีคนเข้าถึงชุดข้อมูลนั้นๆ เช่น เรียกใช้ api หรือดาวน์โหลดไฟล์
    *** ในกรณีที่เป็น Super Admin จะต้องได้รับการแจ้งเตือนทุกอย่างภายในระบบ
    """
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        # Fetch dataset details
        cursor.execute("SELECT service_name, created_by, contact_email FROM service WHERE service_id = %s", (service_id,))
        svc = cursor.fetchone()
        if not svc:
            cursor.close()
            conn.close()
            return

        service_name, created_by, contact_email = svc
        svc_title = service_name or f"ID {service_id}"

        # Determine actor display name
        actor_name = "ผู้ใช้งานทั่วไป (Guest)"
        actor_id_int = None
        if actor_user_id:
            try:
                actor_id_int = int(actor_user_id)
            except (ValueError, TypeError):
                actor_id_int = None

        if actor_id_int and actor_id_int > 0:
            cursor.execute("SELECT username, firstname, lastname FROM user WHERE user_id = %s", (actor_id_int,))
            u_row = cursor.fetchone()
            if u_row:
                full_name = f"{u_row[1] or ''} {u_row[2] or ''}".strip()
                actor_name = full_name if full_name else (u_row[0] or f"User {actor_id_int}")

        # Recipients: Super Admins + Dataset Creator
        cursor.execute("SELECT user_id FROM user WHERE previlage_id = 4 AND status_account = 'active'")
        recipients = {row[0] for row in cursor.fetchall() if row[0]}

        if created_by:
            recipients.add(created_by)
        if contact_email:
            cursor.execute("SELECT user_id FROM user WHERE LOWER(email) = LOWER(%s) AND status_account = 'active'", (contact_email.strip(),))
            c_row = cursor.fetchone()
            if c_row and c_row[0]:
                recipients.add(c_row[0])

        # Do not notify the actor themselves about their own action
        if actor_id_int:
            recipients.discard(actor_id_int)

        if not recipients:
            cursor.close()
            conn.close()
            return

        # Prepare message and notification type
        if access_method == 'download':
            notif_type = 'dataset_file_download'
            file_desc = f" ({detail})" if detail else ""
            message = f'ผู้ใช้ "{actor_name}" ได้ดาวน์โหลดไฟล์{file_desc}ของชุดข้อมูล "{svc_title}"'
        else:
            notif_type = 'dataset_api_access'
            message = f'ผู้ใช้ "{actor_name}" ได้เรียกใช้งาน API ของชุดข้อมูล "{svc_title}"'

        # Throttle / Anti-spam: check if notification of this type for this dataset was sent to recipient in last 60 seconds
        placeholders = ', '.join(['%s'] * len(recipients))
        cursor.execute(f"""
            SELECT user_id FROM notifications 
            WHERE user_id IN ({placeholders}) 
              AND type = %s 
              AND message = %s 
              AND created_at >= NOW() - INTERVAL 60 SECOND
        """, list(recipients) + [notif_type, message])
        throttled_users = {row[0] for row in cursor.fetchall()}

        for uid in recipients:
            if uid not in throttled_users:
                cursor.execute("INSERT INTO notifications (user_id, type, message) VALUES (%s, %s, %s)", (uid, notif_type, message))

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Failed to notify dataset access:", e)
