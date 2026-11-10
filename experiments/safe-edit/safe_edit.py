"""Prototype: unique literal edit of one known UTF-8 file under a Windows exclusive handle."""
import ast
import ctypes
from ctypes import wintypes
import json
import msvcrt
import os
from pathlib import Path
import sys

KERNEL = ctypes.WinDLL('kernel32', use_last_error=True)
KERNEL.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
KERNEL.CreateFileW.restype = wintypes.HANDLE
INVALID = ctypes.c_void_p(-1).value


def open_exclusive(path):
    handle = KERNEL.CreateFileW(str(path), 0x80000000 | 0x40000000, 0, None, 3, 0x80 | 0x00200000, None)
    if handle == INVALID:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return os.fdopen(msvcrt.open_osfhandle(handle, os.O_RDWR | os.O_BINARY), 'r+b', buffering=0)
    except BaseException:
        KERNEL.CloseHandle(handle)
        raise


def apply(root, old, new):
    root = Path(root).resolve(strict=True)
    path = root / 'txreconcile.py'
    if path.is_symlink() or (hasattr(os.path, 'isjunction') and os.path.isjunction(path)):
        raise ValueError('link target is not allowed')
    if not isinstance(old, str) or not old or not isinstance(new, str) or old == new:
        raise ValueError('old and new must be distinct strings, old nonempty')
    with open_exclusive(path) as f:
        original = f.read()
        text = original.decode('utf-8', errors='strict')
        if text.count(old) != 1:
            raise ValueError('old text must occur exactly once (literal match only)')
        candidate = text.replace(old, new, 1)
        ast.parse(candidate, filename=str(path))
        encoded = candidate.encode('utf-8')
        try:
            f.seek(0)
            written = f.write(encoded)
            if written != len(encoded):
                raise OSError('short write')
            f.truncate()
            f.flush()
            os.fsync(f.fileno())
        except Exception:
            try:
                f.seek(0)
                f.write(original)
                f.truncate()
                f.flush()
                os.fsync(f.fileno())
            except Exception as rollback:
                raise RuntimeError('write failed and restoration failed: ' + str(rollback))
            raise
    return 'Applied one exact replacement after syntax validation.'


if __name__ == '__main__':
    try:
        data = json.load(sys.stdin)
        print(json.dumps({'ok': True, 'message': apply(os.getcwd(), data['oldString'], data['newString'])}))
    except Exception as e:
        print(json.dumps({'ok': False, 'error': type(e).__name__ + ': ' + str(e)}))
        sys.exit(1)
