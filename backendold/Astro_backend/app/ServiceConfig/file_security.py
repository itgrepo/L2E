# -*- coding: utf-8 -*-
"""
Central File Upload Security & Sanitization Module
Protects against:
- Malicious PDF payloads (JavaScript, Launch action, EmbeddedFiles, RichMedia)
- Image decompression bombs, metadata payloads, polyglots (re-encodes images cleanly)
- Zip bombs, directory traversal, nested archives, symlinks
- Fake extensions, fake MIME types, double extensions, null-byte filenames
- Executable or script content disguised as documents/images
"""

import os
import io
import re
import uuid
import logging
import zipfile
import base64
from datetime import datetime

# Setup logger
logger = logging.getLogger("file_security")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] [SECURITY] [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Optional Pillow & pypdf with fallback
try:
    from PIL import Image, ImageOps
    # Limit max pixels to prevent Decompression Bomb (25 Megapixels)
    Image.MAX_IMAGE_PIXELS = 25000000
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    try:
        from PyPDF2 import PdfReader
        HAS_PYPDF = True
    except ImportError:
        HAS_PYPDF = False


# Dangerous extensions that should NEVER appear anywhere in a filename (especially double extensions)
DANGEROUS_EXTENSIONS = {
    'php', 'php3', 'php4', 'php5', 'php7', 'phtml', 'phar', 'inc',
    'exe', 'dll', 'com', 'bat', 'cmd', 'sh', 'bash', 'zsh', 'ps1', 'vbs', 'vbe', 'wsf', 'wsh',
    'py', 'pyc', 'pyo', 'pyd', 'rb', 'pl', 'cgi', 'jsp', 'jspx', 'asp', 'aspx', 'cer', 'asa',
    'htaccess', 'htpasswd', 'ini', 'config', 'env',
    'js', 'mjs', 'jsx', 'ts', 'tsx', 'html', 'htm', 'xhtml', 'svg', 'svgz', 'swf'
}

# Allowlist by Category
CATEGORY_ALLOWLIST = {
    'mou': {'pdf', 'png', 'jpg', 'jpeg', 'webp'},
    'attachment': {'pdf', 'png', 'jpg', 'jpeg', 'webp'},
    'service_image': {'png', 'jpg', 'jpeg', 'webp'},
    'data_file': {'csv', 'xlsx', 'xls', 'json', 'xml'},
    'dictionary_file': {'csv', 'xlsx', 'xls'},
    'sampling_file': {'zip'}
}

# MIME Types Allowlist
SAFE_MIME_TYPES = {
    'pdf': 'application/pdf',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'webp': 'image/webp',
    'csv': 'text/csv',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'xls': 'application/vnd.ms-excel',
    'json': 'application/json',
    'xml': 'application/xml',
    'zip': 'application/zip'
}


def log_upload_rejection(user_id, orig_filename, detected_type, reason):
    """Safely logs upload rejection event without leaking file contents or secrets."""
    try:
        safe_name = sanitize_filename(orig_filename or 'unknown')[0]
    except Exception:
        safe_name = 'malformed_filename'
    logger.warning(
        f"UPLOAD REJECTED | UserID: {user_id or 'anonymous'} | File: '{safe_name}' | "
        f"Detected: {detected_type or 'unknown'} | Reason: {reason}"
    )


def sanitize_filename(filename):
    """
    Sanitizes filename against path traversal, null bytes, control chars, and double extensions.
    Returns (safe_display_name, extension)
    """
    if not filename or not isinstance(filename, str):
        return ('unnamed_file', '')

    # 1. Reject Null bytes and control characters
    if '\x00' in filename or '%00' in filename:
        raise ValueError('ชื่อไฟล์มีอักขระที่ไม่ปลอดภัย (Null Byte Detected)')

    # 2. Extract basename (strip directory traversal like ../, ..\, absolute paths)
    clean = os.path.basename(filename).strip()
    clean = re.sub(r'[\r\n\t\x00-\x1f\x7f-\x9f]', '', clean)
    clean = clean.replace('\\', '/').split('/')[-1]

    if not clean or clean in ('.', '..'):
        return ('unnamed_file', '')

    # 3. Check for Dangerous Double Extensions (e.g. test.php.png, exploit.exe.pdf)
    parts = clean.lower().split('.')
    if len(parts) > 2:
        # Check all middle segments for dangerous executable/script extensions
        for part in parts[1:-1]:
            if part in DANGEROUS_EXTENSIONS:
                raise ValueError(f'ไม่อนุญาตให้อัปโหลดไฟล์ที่มีนามสกุลซ้อนอันตราย (Double Extension: .{part})')

    ext = parts[-1] if len(parts) > 1 else ''
    
    # Check final extension against dangerous list
    if ext in DANGEROUS_EXTENSIONS:
        raise ValueError(f'ไม่อนุญาตให้อัปโหลดไฟล์ประเภท .{ext}')

    # Sanitize characters in display name
    safe_chars = re.sub(r'[^a-zA-Z0-9_\-\.\u0E00-\u0E7F]', '_', clean)
    safe_chars = re.sub(r'_+', '_', safe_chars)

    return (safe_chars, ext)


TYPE_DISPLAY_NAMES = {
    'pdf': 'PDF Document (.pdf)',
    'png': 'PNG Image (.png)',
    'jpeg': 'JPEG Image (.jpg/.jpeg)',
    'webp': 'WebP Image (.webp)',
    'zip': 'ZIP Archive (.zip)',
    'xlsx': 'Excel OpenXML (.xlsx)',
    'xls': 'Excel Binary (.xls)',
    'csv': 'CSV / Tabular Data (.csv)',
    'json': 'JSON Document (.json)',
    'xml': 'XML Document (.xml)',
    'svg': 'SVG Vector Image (.svg - ไม่อนุญาต)',
    'php_script': 'PHP Script (ไม่อนุญาต)',
    'html_script': 'HTML / Web Script (ไม่อนุญาต)',
    'malicious_script': 'Script / Web Code (ไม่อนุญาต)',
    'executable': 'Executable / Program Script (ไม่อนุญาต)',
    'plain_text': 'Plain Text (ข้อความธรรมดา)',
    'unknown': 'ไม่ทราบชนิดข้อมูล / ข้อมูลเสียหาย (Unknown/Corrupted Binary)'
}


def detect_csv_structure(text_sample):
    """
    Checks if text sample looks like structured tabular CSV data.
    Must have at least 1-2 lines with consistent delimiters (comma, semicolon, tab, pipe).
    """
    lines = [line.strip() for line in text_sample.splitlines() if line.strip()]
    if not lines:
        return False
    
    # Check for common delimiters
    for delim in [',', ';', '\t', '|']:
        counts = [line.count(delim) for line in lines[:5]]
        if counts and counts[0] >= 1:
            if len(counts) == 1:
                return True
            if all(c == counts[0] for c in counts[1:]):
                return True
            if sum(1 for c in counts if c > 0) >= len(counts) * 0.7:
                return True
    return False


def detect_file_signature(file_bytes):
    """
    Reads initial bytes (magic numbers) to accurately detect the true file format.
    Returns format string: 'pdf', 'png', 'jpeg', 'webp', 'zip', 'csv', 'xlsx', 'xls', 'json', 'xml', 'plain_text', 'svg', 'php_script', 'html_script', 'executable', or 'unknown'
    """
    if not file_bytes or len(file_bytes) < 4:
        return 'unknown'

    # 1. PDF: %PDF- (offset 0)
    if file_bytes.startswith(b'%PDF-'):
        return 'pdf'

    # 2. PNG: \x89PNG\r\n\x1a\n (offset 0)
    if file_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'

    # 3. JPEG: \xff\xd8\xff (offset 0)
    if file_bytes.startswith(b'\xff\xd8\xff'):
        return 'jpeg'

    # 4. WEBP: RIFF....WEBP
    if file_bytes.startswith(b'RIFF') and len(file_bytes) >= 12 and file_bytes[8:12] == b'WEBP':
        return 'webp'

    # 5. ZIP / XLSX: PK\x03\x04
    if file_bytes.startswith(b'PK\x03\x04') or file_bytes.startswith(b'PK\x05\x06') or file_bytes.startswith(b'PK\x07\x08'):
        # Check if it's an OpenXML XLSX
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
                namelist = zf.namelist()
                if '[Content_Types].xml' in namelist and any('xl/' in n for n in namelist):
                    return 'xlsx'
        except Exception:
            pass
        return 'zip'

    # 6. Old Excel XLS (Compound Binary File Format): \xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1
    if file_bytes.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
        return 'xls'

    # 7. Executables / Scripts detection (MZ, ELF, Script headers) -> reject immediately
    if file_bytes.startswith(b'MZ') or file_bytes.startswith(b'\x7fELF') or file_bytes.startswith(b'#!'):
        return 'executable'

    # 8. HTML / XML / SVG / PHP checks
    header_sample = file_bytes[:2048].lower()
    if b'<?php' in header_sample:
        return 'php_script'
    if b'<svg' in header_sample or (b'<?xml' in header_sample and b'<svg' in file_bytes[:4096].lower()):
        return 'svg'
    if b'<html' in header_sample or b'<!doctype html' in header_sample or b'<script' in header_sample or b'<body' in header_sample:
        return 'html_script'

    # 9. JSON detection
    stripped = file_bytes.strip()
    if (stripped.startswith(b'{') and stripped.endswith(b'}')) or (stripped.startswith(b'[') and stripped.endswith(b']')):
        try:
            import json
            json.loads(file_bytes.decode('utf-8'))
            return 'json'
        except Exception:
            pass

    # 10. XML detection
    if stripped.startswith(b'<?xml') or (stripped.startswith(b'<') and stripped.endswith(b'>')):
        if b'<script' not in header_sample and b'<svg' not in header_sample:
            return 'xml'

    # 11. Plain text vs CSV detection
    try:
        sample = file_bytes[:8192]
        if b'\x00' not in sample:
            decoded = None
            try:
                decoded = sample.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    decoded = sample.decode('cp874')
                except UnicodeDecodeError:
                    pass

            if decoded:
                if detect_csv_structure(decoded):
                    return 'csv'
                else:
                    return 'plain_text'
    except Exception:
        pass

    return 'unknown'


def check_polyglot_and_embedded_scripts(file_bytes, expected_type):
    """
    Checks for polyglot files (e.g. PNG containing valid PDF/ZIP/PHP headers or payloads).
    """
    sample = file_bytes[:4096].lower()
    
    # 1. Disallow HTML / JavaScript / PHP tags in binary images or documents
    dangerous_tags = [b'<?php', b'<script', b'javascript:', b'eval(', b'base64_decode', b'shell_exec', b'system(']
    for tag in dangerous_tags:
        if tag in sample:
            raise ValueError('ตรวจพบลักษณะโค้ดหรือสคริปต์ที่ไม่อนุญาตในไฟล์')

    # 2. Check for conflicting binary magic numbers (e.g. PDF header inside PNG or vice-versa)
    if expected_type in ('png', 'jpeg', 'webp'):
        if b'%PDF-' in file_bytes:
            raise ValueError('ตรวจพบลักษณะไฟล์ซ้อนทับ (Polyglot PNG/PDF) ไม่อนุญาตให้อัปโหลด')
        if b'PK\x03\x04' in file_bytes[:1024]:
            raise ValueError('ตรวจพบลักษณะไฟล์ซ้อนทับ (Polyglot Image/ZIP) ไม่อนุญาตให้อัปโหลด')

    if expected_type == 'pdf':
        if file_bytes.startswith(b'\x89PNG') or file_bytes.startswith(b'\xff\xd8\xff'):
            raise ValueError('ตรวจพบลักษณะไฟล์ซ้อนทับ (Polyglot PDF/Image) ไม่อนุญาตให้อัปโหลด')


def validate_image_security(file_bytes, ext, max_size_mb=10, max_pixels=25000000, max_dim=5000):
    """
    Validates and re-encodes images to sanitize EXIF, comments, and trailing payloads.
    Returns sanitized clean bytes.
    """
    # 1. Size check
    if len(file_bytes) > max_size_mb * 1024 * 1024:
        raise ValueError(f'ขนาดไฟล์รูปภาพเกินกำหนด ({max_size_mb} MB)')

    # 2. Check polyglot / script injection
    check_polyglot_and_embedded_scripts(file_bytes, ext)

    if not HAS_PIL:
        sig = detect_file_signature(file_bytes)
        if sig not in ('png', 'jpeg', 'webp'):
            raise ValueError('โครงสร้างไฟล์รูปภาพไม่ถูกต้อง')
        return file_bytes

    # 3. Parse with Pillow
    try:
        img_buffer = io.BytesIO(file_bytes)
        with Image.open(img_buffer) as img:
            img.verify()  # Verify image integrity
    except Exception as e:
        raise ValueError('ไม่สามารถอ่านไฟล์รูปภาพได้ หรือไฟล์รูปภาพมีความเสียหาย')

    # 4. Re-open to read dimensions, pixels, and re-encode
    try:
        img_buffer = io.BytesIO(file_bytes)
        with Image.open(img_buffer) as img:
            width, height = img.size
            if width > max_dim or height > max_dim:
                raise ValueError(f'ขนาดรูปภาพเกินกำหนด (สูงสุด {max_dim}x{max_dim} พิกเซล, ขนาดไฟล์จริง: {width}x{height})')
            
            if (width * height) > max_pixels:
                raise ValueError('จำนวนพิกเซลของรูปภาพเกินกำหนด (Decompression Bomb Protection)')

            # Prepare format for re-encoding
            target_format = 'PNG' if ext == 'png' else ('WEBP' if ext == 'webp' else 'JPEG')
            
            output_buffer = io.BytesIO()
            if target_format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                clean_img = img.convert('RGB')
                clean_img.save(output_buffer, format='JPEG', quality=90, optimize=True)
            elif target_format == 'PNG':
                clean_img = img.copy()
                clean_img.save(output_buffer, format='PNG', optimize=True)
            elif target_format == 'WEBP':
                clean_img = img.copy()
                clean_img.save(output_buffer, format='WEBP', quality=90)
            else:
                clean_img = img.convert('RGB')
                clean_img.save(output_buffer, format='JPEG', quality=90)

            clean_bytes = output_buffer.getvalue()
            return clean_bytes

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f'เกิดข้อผิดพลาดในการประมวลผลรูปภาพ: {str(e)}')


def validate_pdf_security(file_bytes, max_size_mb=10, max_pages=100):
    """
    Validates PDF signature and scans structure for dangerous actions, JavaScript, and embedded files.
    Returns clean validated bytes.
    """
    # 1. Size check
    if len(file_bytes) > max_size_mb * 1024 * 1024:
        raise ValueError(f'ขนาดไฟล์ PDF เกินกำหนด ({max_size_mb} MB)')

    # 2. Signature check: Must start with %PDF- at offset 0
    if not file_bytes.startswith(b'%PDF-'):
        raise ValueError('ไฟล์เอกสารไม่มีโครงสร้าง Header ของ PDF ที่ถูกต้อง')

    # 3. Check for polyglot / script injection
    check_polyglot_and_embedded_scripts(file_bytes, 'pdf')

    # 4. Byte-level AST scan for dangerous PDF tokens
    dangerous_tokens = [
        (rb'/JavaScript\b', 'ตรวจพบ JavaScript ภายในไฟล์ PDF (ไม่อนุญาต)'),
        (rb'/JS\b', 'ตรวจพบคำสั่ง JavaScript (JS) ภายในไฟล์ PDF (ไม่อนุญาต)'),
        (rb'/Launch\b', 'ตรวจพบคำสั่ง Launch Action ภายในไฟล์ PDF (ไม่อนุญาต)'),
        (rb'/EmbeddedFiles\b', 'ตรวจพบไฟล์แนบฝังใน PDF (EmbeddedFiles) (ไม่อนุญาต)'),
        (rb'/EF\b', 'ตรวจพบ Embedded File Streams (EF) ภายในไฟล์ PDF (ไม่อนุญาต)'),
        (rb'/RichMedia\b', 'ตรวจพบ RichMedia / Flash ภายในไฟล์ PDF (ไม่อนุญาต)'),
        (rb'/SubmitForm\b', 'ตรวจพบคำสั่งส่งฟอร์มข้อมูล (SubmitForm) ภายในไฟล์ PDF (ไม่อนุญาต)'),
        (rb'/ImportData\b', 'ตรวจพบคำสั่งนำเข้าข้อมูล (ImportData) ภายในไฟล์ PDF (ไม่อนุญาต)'),
    ]

    for pattern, err_msg in dangerous_tokens:
        if re.search(pattern, file_bytes, re.IGNORECASE):
            raise ValueError(err_msg)

    # 5. Parse with pypdf / PyPDF2 if available
    if HAS_PYPDF:
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            num_pages = len(reader.pages)
            if num_pages > max_pages:
                raise ValueError(f'จำนวนหน้าของเอกสาร PDF เกินกำหนด (สูงสุด {max_pages} หน้า, ไฟล์จริงมี {num_pages} หน้า)')
            if num_pages == 0:
                raise ValueError('เอกสาร PDF ไม่มีหน้าข้อมูล')

            # Deep check catalog / root dictionary
            trailer = reader.trailer
            if trailer:
                root = trailer.get('/Root', {})
                if hasattr(root, 'get_object'):
                    root = root.get_object()
                
                # Check for /OpenAction or /AA containing JavaScript
                if '/OpenAction' in root:
                    open_action = root['/OpenAction']
                    if hasattr(open_action, 'get_object'):
                        open_action = open_action.get_object()
                    if isinstance(open_action, dict) and ('/S' in open_action or '/JS' in open_action):
                        action_type = str(open_action.get('/S', ''))
                        if 'JavaScript' in action_type or 'Launch' in action_type or '/JS' in open_action:
                            raise ValueError('ตรวจพบ OpenAction ที่มีสคริปต์ใน PDF')

                # Check /Names for JavaScript dictionary
                if '/Names' in root:
                    names = root['/Names']
                    if hasattr(names, 'get_object'):
                        names = names.get_object()
                    if isinstance(names, dict) and ('/JavaScript' in names or '/EmbeddedFiles' in names):
                        raise ValueError('ตรวจพบ Embedded Names / JavaScript Dictionary ใน PDF')

        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f'ไฟล์ PDF มีโครงสร้างผิดปกติหรือไม่สามารถเปิดอ่านได้: {str(e)}')

    return file_bytes


def validate_zip_security(file_bytes, max_uncompressed_mb=50, max_files=100, max_ratio=10):
    """
    Validates ZIP archive against Zip Bombs, path traversal, nested archives, and symlinks.
    Returns clean validated bytes.
    """
    if not file_bytes.startswith(b'PK\x03\x04') and not file_bytes.startswith(b'PK\x05\x06'):
        raise ValueError('ไฟล์ไม่ใช่โครงสร้าง ZIP Archive ที่ถูกต้อง')

    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
            infolist = zf.infolist()
            
            if len(infolist) > max_files:
                raise ValueError(f'จำนวนไฟล์ภายใน ZIP เกินกำหนด (สูงสุด {max_files} ไฟล์, พบ {len(infolist)} ไฟล์)')

            total_uncompressed_size = 0
            for info in infolist:
                # 1. Path Traversal & dangerous filename check
                fname = info.filename
                if '\x00' in fname or '..' in fname or fname.startswith('/') or fname.startswith('\\'):
                    raise ValueError(f'พบชื่อไฟล์ที่ไม่ปลอดภัยใน ZIP (Path Traversal): {fname}')

                # 2. Check extension
                sub_ext = fname.rsplit('.', 1)[-1].lower() if '.' in fname else ''
                if sub_ext in DANGEROUS_EXTENSIONS:
                    raise ValueError(f'พบไฟล์ประเภทอันตรายภายใน ZIP (.{sub_ext}): {fname}')

                # 3. Check for nested archives
                if sub_ext in ('zip', 'tar', 'gz', 'rar', '7z', 'bz2', 'xz'):
                    raise ValueError(f'ไม่อนุญาตให้มีไฟล์บีบอัดซ้อนภายใน ZIP (Nested Archive): {fname}')

                # 4. Check for symlinks (Unix external_attr & 0o120000)
                if (info.external_attr >> 16) & 0o120000 == 0o120000:
                    raise ValueError(f'พบ Symlink ภายใน ZIP (ไม่อนุญาต): {fname}')

                total_uncompressed_size += info.file_size

            # 5. Check total uncompressed size and compression ratio (Anti-Zip Bomb)
            max_bytes = max_uncompressed_mb * 1024 * 1024
            if total_uncompressed_size > max_bytes:
                raise ValueError(f'ขนาดข้อมูลเมื่อแตกไฟล์ ZIP เกินกำหนด ({max_uncompressed_mb} MB)')

            compressed_size = max(len(file_bytes), 1)
            ratio = total_uncompressed_size / compressed_size
            if ratio > max_ratio and total_uncompressed_size > 5 * 1024 * 1024:
                raise ValueError('อัตราการบีบอัดไฟล์ ZIP สูงผิดปกติ (Zip Bomb Protection)')

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f'ไฟล์ ZIP มีโครงสร้างผิดปกติหรือไม่สามารถเปิดอ่านได้: {str(e)}')

    return file_bytes


def validate_tabular_security(file_bytes, ext, max_size_mb=50):
    """
    Validates CSV, XLSX, XLS, JSON, XML data files.
    """
    if len(file_bytes) > max_size_mb * 1024 * 1024:
        raise ValueError(f'ขนาดไฟล์ข้อมูลเกินกำหนด ({max_size_mb} MB)')

    sig = detect_file_signature(file_bytes)
    
    if ext == 'csv':
        if sig not in ('csv', 'unknown'):
            if sig in ('executable', 'malicious_script', 'pdf', 'png', 'jpeg', 'zip'):
                raise ValueError('เนื้อหาของไฟล์ไม่ใช่ CSV ที่ถูกต้อง')
    elif ext == 'xlsx':
        if sig != 'xlsx':
            raise ValueError('เนื้อหาของไฟล์ไม่ใช่ Excel (.xlsx) ที่ถูกต้อง')
    elif ext == 'xls':
        if sig != 'xls':
            raise ValueError('เนื้อหาของไฟล์ไม่ใช่ Excel (.xls) ที่ถูกต้อง')
    elif ext == 'json':
        if sig != 'json':
            raise ValueError('เนื้อหาของไฟล์ไม่ใช่ JSON ที่ถูกต้อง')
    elif ext == 'xml':
        if sig != 'xml':
            raise ValueError('เนื้อหาของไฟล์ไม่ใช่ XML ที่ถูกต้อง')

    return file_bytes


def validate_and_sanitize_upload(file_input, category='mou', max_size_mb=10, user_id=None, orig_filename=None):
    """
    Master validator function.
    Accepts:
      - werkzeug FileStorage object
      - raw bytes
      - base64 string
    Returns:
      (success: bool, clean_bytes: bytes, saved_filename: str, clean_orig_name: str, error_message: str)
    """
    detected_sig = 'unknown'
    raw_name = orig_filename or ''
    try:
        # 1. Extract raw bytes and original filename
        raw_bytes = None

        if hasattr(file_input, 'read') and hasattr(file_input, 'filename'):
            raw_name = file_input.filename
            raw_bytes = file_input.read()
        elif isinstance(file_input, bytes):
            raw_bytes = file_input
        elif isinstance(file_input, str):
            # Base64 string handling
            if ',' in file_input:
                header, base64_data = file_input.split(',', 1)
            else:
                base64_data = file_input
            raw_bytes = base64.b64decode(base64_data)
        else:
            raise ValueError('รูปแบบข้อมูลไฟล์ไม่ถูกต้อง')

        if not raw_bytes or len(raw_bytes) == 0:
            raise ValueError('ไฟล์ไม่มีข้อมูล (0 Bytes)')

        # 2. Sanitize original filename and check double extensions
        clean_orig_name, declared_ext = sanitize_filename(raw_name)
        declared_ext = declared_ext.lower()

        if not declared_ext:
            raise ValueError('ไม่พบส่วนขยาย (Extension) ของไฟล์')

        # 3. Allowlist check for Category
        allowlist = CATEGORY_ALLOWLIST.get(category, {'pdf', 'png', 'jpg', 'jpeg', 'webp'})
        if declared_ext not in allowlist:
            allowed_str = ', '.join([f'.{e}' for e in sorted(allowlist)])
            raise ValueError(f'นามสกุลไฟล์ .{declared_ext} ไม่ได้รับอนุญาตสำหรับหมวดหมู่นี้ (รองรับเฉพาะ {allowed_str})')

        # 4. Detect real magic byte signature
        detected_sig = detect_file_signature(raw_bytes)
        
        # Check signature compatibility with declared extension
        ext_to_sig_map = {
            'pdf': 'pdf',
            'png': 'png',
            'jpg': 'jpeg',
            'jpeg': 'jpeg',
            'webp': 'webp',
            'zip': 'zip',
            'xlsx': 'xlsx',
            'xls': 'xls',
            'csv': 'csv',
            'json': 'json',
            'xml': 'xml'
        }

        expected_sig = ext_to_sig_map.get(declared_ext)
        if expected_sig and detected_sig != expected_sig:
            if declared_ext == 'csv' and detected_sig in ('csv', 'plain_text', 'unknown'):
                pass
            else:
                detected_label = TYPE_DISPLAY_NAMES.get(detected_sig, detected_sig)
                raise ValueError(f'ชนิดไฟล์จริง ({detected_label}) ไม่ตรงกับนามสกุลไฟล์ที่ระบุ (.{declared_ext})')

        # 5. Deep inspection and Sanitization based on type
        clean_bytes = None
        if declared_ext in ('png', 'jpg', 'jpeg', 'webp'):
            clean_bytes = validate_image_security(raw_bytes, declared_ext, max_size_mb=max_size_mb)
        elif declared_ext == 'pdf':
            clean_bytes = validate_pdf_security(raw_bytes, max_size_mb=max_size_mb)
        elif declared_ext == 'zip':
            clean_bytes = validate_zip_security(raw_bytes)
        elif declared_ext in ('csv', 'xlsx', 'xls', 'json', 'xml'):
            clean_bytes = validate_tabular_security(raw_bytes, declared_ext, max_size_mb=max_size_mb)
        else:
            raise ValueError('ประเภทไฟล์ไม่รองรับการตรวจสอบความปลอดภัย')

        # 6. Generate secure UUID filename for on-disk storage (NEVER use user input as path)
        secure_uuid = uuid.uuid4().hex
        saved_filename = f"{secure_uuid}.{declared_ext}"

        return (True, clean_bytes, saved_filename, clean_orig_name, '')

    except Exception as e:
        error_msg = str(e)
        log_upload_rejection(user_id, raw_name, detected_sig, error_msg)
        return (False, None, '', '', error_msg)
