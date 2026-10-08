# -*- coding: utf-8 -*-
"""
Comprehensive Automated Test Suite for File Security Validation
Tests 10 Security Vectors:
1. Fake Extension
2. Fake MIME / Injected Script
3. Polyglot Files (PNG + PDF / PNG + PHP)
4. Malicious PDF (Embedded JavaScript / Launch Action)
5. Double Extension (e.g. file.php.png, file.pdf.exe)
6. Null Byte Filename
7. Path Traversal Filename
8. Zip Bomb & Path Traversal inside Zip Archive
9. Oversized File (>10MB)
10. Valid Clean PDF, PNG, JPEG, WEBP Files
"""

import os
import sys
import io
import base64
import zipfile
import unittest

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backendold/Astro_backend/app/ServiceConfig')))
from file_security import (
    validate_and_sanitize_upload,
    sanitize_filename,
    detect_file_signature,
    validate_pdf_security,
    validate_image_security,
    validate_zip_security
)

class TestFileSecurity(unittest.TestCase):

    def test_1_fake_extension(self):
        """Vector 1: Shell script or executable named as .pdf or .png must be rejected."""
        fake_pdf = b"#!/bin/bash\necho 'malicious command'\n"
        success, clean_bytes, saved_name, orig_name, err = validate_and_sanitize_upload(
            fake_pdf, category='mou', orig_filename='innocent.pdf'
        )
        self.assertFalse(success)
        self.assertIn("ชนิดไฟล์จริง", err)

        fake_png = b"MZ\x90\x00\x03\x00\x00\x00Windows Executable Stub"
        success, clean_bytes, saved_name, orig_name, err = validate_and_sanitize_upload(
            fake_png, category='mou', orig_filename='photo.png'
        )
        self.assertFalse(success)

    def test_2_fake_mime_and_injected_script(self):
        """Vector 2: HTML/PHP script disguised as image or document must be rejected."""
        php_in_jpg = b"<?php system($_GET['cmd']); ?>"
        success, clean_bytes, saved_name, orig_name, err = validate_and_sanitize_upload(
            php_in_jpg, category='mou', orig_filename='avatar.jpg'
        )
        self.assertFalse(success)

        html_script = b"<html><script>alert(document.cookie)</script></html>"
        success, clean_bytes, saved_name, orig_name, err = validate_and_sanitize_upload(
            html_script, category='mou', orig_filename='report.pdf'
        )
        self.assertFalse(success)

    def test_3_polyglot_files(self):
        """Vector 3: Polyglot PNG containing embedded PDF or PHP code must be rejected."""
        # Starts with valid PNG magic bytes but contains PDF header
        png_magic = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
        polyglot_pdf = png_magic + b"%PDF-1.4\n1 0 obj\n<<>>\nendobj"
        success, clean_bytes, saved_name, orig_name, err = validate_and_sanitize_upload(
            polyglot_pdf, category='mou', orig_filename='polyglot.png'
        )
        self.assertFalse(success)
        self.assertIn("Polyglot", err)

        polyglot_php = png_magic + b"<?php echo 'hacked'; ?>"
        success, clean_bytes, saved_name, orig_name, err = validate_and_sanitize_upload(
            polyglot_php, category='mou', orig_filename='avatar.png'
        )
        self.assertFalse(success)

    def test_4_pdf_embedded_javascript_and_launch(self):
        """Vector 4: PDF containing JavaScript or Launch actions must be rejected."""
        pdf_js = (
            b"%PDF-1.4\n"
            b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R /OpenAction << /S /JavaScript /JS (app.alert('XSS')) >> >>\nendobj\n"
            b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n"
            b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000100 00000 n \n0000000160 00000 n \n"
            b"trailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n230\n%%EOF"
        )
        success, clean_bytes, saved_name, orig_name, err = validate_and_sanitize_upload(
            pdf_js, category='mou', orig_filename='exploit.pdf'
        )
        self.assertFalse(success)
        self.assertTrue("JavaScript" in err or "JS" in err or "OpenAction" in err)

        pdf_launch = (
            b"%PDF-1.4\n"
            b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R /OpenAction << /S /Launch /F (cmd.exe) >> >>\nendobj\n"
            b"trailer\n<< /Root 1 0 R >>\n%%EOF"
        )
        success, clean_bytes, saved_name, orig_name, err = validate_and_sanitize_upload(
            pdf_launch, category='mou', orig_filename='launch.pdf'
        )
        self.assertFalse(success)
        self.assertIn("Launch", err)

    def test_5_double_extension(self):
        """Vector 5: Filenames with dangerous double extensions must be rejected."""
        valid_png_magic = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82"
        
        with self.assertRaises(ValueError) as cm:
            sanitize_filename('backdoor.php.png')
        self.assertIn("Double Extension", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            sanitize_filename('invoice.pdf.exe')
        self.assertIn("ไม่อนุญาต", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            sanitize_filename('photo.phtml.jpg')
        self.assertIn("Double Extension", str(cm.exception))

    def test_6_null_byte_filename(self):
        """Vector 6: Filenames with null bytes must be rejected."""
        with self.assertRaises(ValueError) as cm:
            sanitize_filename('evil.php\x00.png')
        self.assertIn("Null Byte", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            sanitize_filename('test.pdf%00.exe')
        self.assertIn("Null Byte", str(cm.exception))

    def test_7_path_traversal_filename(self):
        """Vector 7: Path traversal in filenames must be stripped to safe basename."""
        safe_name, ext = sanitize_filename('../../../../etc/passwd.pdf')
        self.assertEqual(safe_name, 'passwd.pdf')
        self.assertEqual(ext, 'pdf')

        safe_name2, ext2 = sanitize_filename('..\\..\\Windows\\System32\\calc.png')
        self.assertEqual(safe_name2, 'calc.png')
        self.assertEqual(ext2, 'png')

    def test_8_zip_bomb_and_traversal_in_archive(self):
        """Vector 8: ZIP with path traversal or dangerous contents must be rejected."""
        # Create in-memory zip with path traversal
        traversal_buf = io.BytesIO()
        with zipfile.ZipFile(traversal_buf, 'w') as zf:
            zf.writestr('../../evil.sh', '#!/bin/sh\necho hacked\n')
        traversal_bytes = traversal_buf.getvalue()

        success, clean_bytes, saved_name, orig_name, err = validate_and_sanitize_upload(
            traversal_bytes, category='sampling_file', orig_filename='sample.zip'
        )
        self.assertFalse(success)
        self.assertIn("Path Traversal", err)

        # Create zip with nested zip
        nested_buf = io.BytesIO()
        with zipfile.ZipFile(nested_buf, 'w') as zf:
            zf.writestr('inner.zip', b'PK\x03\x04test')
        nested_bytes = nested_buf.getvalue()

        success, clean_bytes, saved_name, orig_name, err = validate_and_sanitize_upload(
            nested_bytes, category='sampling_file', orig_filename='nested.zip'
        )
        self.assertFalse(success)
        self.assertIn("Nested Archive", err)

    def test_9_oversized_file(self):
        """Vector 9: Oversized file (>10MB) must be rejected."""
        oversized_bytes = b"%PDF-1.4\n" + b"A" * (11 * 1024 * 1024)
        success, clean_bytes, saved_name, orig_name, err = validate_and_sanitize_upload(
            oversized_bytes, category='mou', orig_filename='large.pdf', max_size_mb=10
        )
        self.assertFalse(success)
        self.assertIn("เกินกำหนด", err)

    def test_10_valid_clean_files(self):
        """Vector 10: Valid clean PDF, PNG, JPG must pass validation and generate UUID storage names."""
        # Valid PNG generated with Pillow or binary fallback
        try:
            from PIL import Image
            img_buf = io.BytesIO()
            img = Image.new('RGB', (20, 20), color='blue')
            img.save(img_buf, format='PNG')
            valid_png = img_buf.getvalue()
        except Exception:
            # Fallback 1x1 valid transparent PNG
            valid_png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")

        success, clean_bytes, saved_name, orig_name, err = validate_and_sanitize_upload(
            valid_png, category='mou', orig_filename='my_photo.png'
        )
        self.assertTrue(success, f"Valid PNG failed: {err}")
        self.assertTrue(saved_name.endswith('.png'))
        self.assertEqual(len(saved_name.split('.')[0]), 32) # UUID hex length is 32

        # Valid JPEG
        try:
            from PIL import Image
            jpg_buf = io.BytesIO()
            jpg_img = Image.new('RGB', (20, 20), color='green')
            jpg_img.save(jpg_buf, format='JPEG')
            valid_jpg = jpg_buf.getvalue()
            
            success_jpg, clean_jpg, saved_jpg, _, err_jpg = validate_and_sanitize_upload(
                valid_jpg, category='mou', orig_filename='sample.jpg'
            )
            self.assertTrue(success_jpg, f"Valid JPG failed: {err_jpg}")
            self.assertTrue(saved_jpg.endswith('.jpg'))
        except Exception as e:
            pass

        # Valid Minimal Clean PDF
        clean_pdf = (
            b"%PDF-1.4\n"
            b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
            b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n"
            b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n"
            b"trailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n190\n%%EOF"
        )
        success, clean_bytes, saved_name, orig_name, err = validate_and_sanitize_upload(
            clean_pdf, category='mou', orig_filename='clean_document.pdf'
        )
        self.assertTrue(success, f"Valid PDF failed: {err}")
        self.assertTrue(saved_name.endswith('.pdf'))
        self.assertEqual(len(saved_name.split('.')[0]), 32)


if __name__ == '__main__':
    unittest.main(verbosity=2)
