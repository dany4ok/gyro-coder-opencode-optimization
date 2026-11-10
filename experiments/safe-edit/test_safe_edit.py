import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import safe_edit


class SafeEditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.root = Path(self.temp.name)
        self.file = self.root / 'txreconcile.py'
        self.file.write_bytes(b'value = 1\n')

    def tearDown(self):
        self.temp.cleanup()

    def test_syntax_rejected_without_writing(self):
        before = self.file.read_bytes()
        with self.assertRaises(SyntaxError):
            safe_edit.apply(self.root, 'value = 1', 'value = (')
        self.assertEqual(self.file.read_bytes(), before)

    def test_valid_edit(self):
        safe_edit.apply(self.root, 'value = 1', 'value = 2')
        self.assertEqual(self.file.read_bytes(), b'value = 2\n')

    def test_ambiguous_missing_and_noop_rejected(self):
        self.file.write_bytes(b'value = 1\nvalue = 1\n')
        before = self.file.read_bytes()
        for old, new in [('value = 1', 'value = 2'), ('not found', 'x'), ('value', 'value')]:
            with self.subTest(old=old), self.assertRaises(ValueError):
                safe_edit.apply(self.root, old, new)
            self.assertEqual(self.file.read_bytes(), before)

    def test_crlf_preserved(self):
        self.file.write_bytes(b'value = 1\r\nother = 3\r\n')
        safe_edit.apply(self.root, 'value = 1', 'value = 2')
        self.assertEqual(self.file.read_bytes(), b'value = 2\r\nother = 3\r\n')

    def test_other_process_cannot_open_during_exclusive_handle(self):
        with safe_edit.open_exclusive(self.file):
            p = subprocess.run([sys.executable, '-c', 'import sys; open(sys.argv[1], "rb").read()', str(self.file)], capture_output=True, text=True, timeout=10)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn('PermissionError', p.stderr)
        self.assertEqual(self.file.read_bytes(), b'value = 1\n')

    def test_existing_external_handle_blocks_edit(self):
        with self.file.open('rb'):
            with self.assertRaises(OSError):
                safe_edit.apply(self.root, 'value = 1', 'value = 2')
        self.assertEqual(self.file.read_bytes(), b'value = 1\n')


if __name__ == '__main__':
    unittest.main()
