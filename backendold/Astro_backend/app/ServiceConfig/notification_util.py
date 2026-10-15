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
    หลักการการแจ้งเตือนกระดิ่ง L2E เมื่อมีการสร้างหรือ Update ชุดข้อมูล:
    1. สาธารณะ (Public) - ทุกคนรับการแจ้งเตือน
    2. ภายในหน่วยงาน (Internal) - เฉพาะ Account In Group / In Org รับการแจ้งเตือน, Account Not In Group ไม่ได้รับ
    3. จำกัดสิทธิ์ (Restricted) - ทุกคนรับการแจ้งเตือน
    4. เฉพาะเจ้าของ (Private/PII) - มีเพียงคนสร้าง Dataset และ Super Admin เท่านั้นที่ได้รับการแจ้งเตือน
    *** คนสร้างชุดข้อมูล และ Super Admin ได้รับการแจ้งเตือนทุกกรณี
    *** ผู้ใช้งานที่ได้รับอนุญาตให้เข้าถึงชุดข้อมูลแล้ว จะได้รับการแจ้งเตือนเมื่อมีการอัปเดตชุดข้อมูลนั้น
    """
    try:
        conn = mysql.connect()
        cursor = conn.cursor()

        # Fetch dataset details
        cursor.execute("""
            SELECT service_name, access_type, organization, l2e_group_id, created_by, contact_email 
            FROM service WHERE service_id = %s
        """, (service_id,))
        svc = cursor.fetchone()
        if not svc:
            cursor.close()
            conn.close()
            return

        service_name, access_type, org_name, l2e_group_id, created_by, contact_email = svc
        access_type_lower = (access_type or 'public').lower().strip()
        svc_title = service_name or f"ID {service_id}"

        # 1. Super Admins (previlage_id = 4) always receive notifications
        cursor.execute("SELECT user_id FROM user WHERE previlage_id = 4 AND status_account = 'active'")
        recipients = {row[0] for row in cursor.fetchall() if row[0]}

        # 2. Dataset creator always receives notification
        if created_by:
            recipients.add(created_by)
        if contact_email:
            cursor.execute("SELECT user_id FROM user WHERE LOWER(email) = LOWER(%s) AND status_account = 'active'", (contact_email.strip(),))
            c_row = cursor.fetchone()
            if c_row and c_row[0]:
                recipients.add(c_row[0])

        # 3. For 'updated' event: Users who have approved access must also be notified
        if event_type == 'updated':
            cursor.execute("""
                SELECT DISTINCT u.user_id 
                FROM user u
                WHERE u.status_account = 'active'
                  AND (
                    u.user_id IN (SELECT user_id FROM dataset_permission_requests WHERE service_id = %s AND status = 'Approved')
                    OR u.user_id IN (SELECT user_id FROM service_user_access WHERE service_id = %s)
                  )
            """, (service_id, service_id))
            for row in cursor.fetchall():
                if row[0]:
                    recipients.add(row[0])

        # 4. Access Type routing:
        if access_type_lower in ['public', 'restricted']:
            # Public & Restricted: All active users get notified
            cursor.execute("SELECT user_id FROM user WHERE status_account = 'active'")
            for row in cursor.fetchall():
                if row[0]:
                    recipients.add(row[0])

        elif access_type_lower == 'internal':
            # Internal: Account In Group / Org receives notification
            # a) Users in the same organization
            if org_name:
                cursor.execute("""
                    SELECT u.user_id FROM user u 
                    JOIN organization o ON u.org_id = o.org_id 
                    WHERE o.org_name = %s AND u.status_account = 'active'
                """, (org_name.strip(),))
                for row in cursor.fetchall():
                    if row[0]:
                        recipients.add(row[0])

            # b) Users in the dataset's assigned group (l2e_group_id or service_group_access)
            if l2e_group_id:
                cursor.execute("""
                    SELECT gud.user_id FROM group_user_detail gud 
                    JOIN user u ON gud.user_id = u.user_id 
                    WHERE gud.group_id = %s AND u.status_account = 'active'
                """, (l2e_group_id,))
                for row in cursor.fetchall():
                    if row[0]:
                        recipients.add(row[0])

            cursor.execute("""
                SELECT gud.user_id FROM service_group_access sga 
                JOIN group_user_detail gud ON sga.group_id = gud.group_id 
                JOIN user u ON gud.user_id = u.user_id 
                WHERE sga.service_id = %s AND u.status_account = 'active'
            """, (service_id,))
            for row in cursor.fetchall():
                if row[0]:
                    recipients.add(row[0])

        elif access_type_lower in ['private', 'pii']:
            # Private: Only creator, Super Admin (and approved users if updated)
            pass

        # Prepare message
        if custom_message:
            message = custom_message
        elif event_type == 'created':
            message = f'มีชุดข้อมูลใหม่เข้าสู่ระบบ: "{svc_title}"'
        else:
            message = f'ชุดข้อมูล "{svc_title}" มีการอัปเดตข้อมูลใหม่'

        notif_type = f'dataset_{event_type}'
        for uid in recipients:
            cursor.execute("INSERT INTO notifications (user_id, type, message) VALUES (%s, %s, %s)", (uid, notif_type, message))

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Failed to notify dataset lifecycle:", e)

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
