# main.py
# Compatibility monkeypatch for hashlib (strip 'usedforsecurity' kwarg and provide openssl_md5 fallback)
import hashlib
_orig_hashlib_new = hashlib.new

def _hashlib_new_compat(name, *args, **kwargs):
    # Remove usedforsecurity if present (some Python/OpenSSL bindings don't accept it)
    if 'usedforsecurity' in kwargs:
        kwargs.pop('usedforsecurity')
    return _orig_hashlib_new(name, *args, **kwargs)

hashlib.new = _hashlib_new_compat

# Provide openssl_md5 compatibility if missing
if not hasattr(hashlib, 'openssl_md5'):
    def _openssl_md5_compat(initial: bytes = b''):
        h = hashlib.md5()
        if initial:
            if isinstance(initial, (bytes, bytearray)):
                h.update(initial)
            else:
                h.update(str(initial).encode('utf-8'))
        return h
    hashlib.openssl_md5 = _openssl_md5_compat

# --- Now normal imports and app startup ---
from auth import LoginWindow
import logging
import sys

def main():
    # Configure logging (DEBUG while we debug)
    logging.basicConfig(
        level=logging.DEBUG,   # changed to DEBUG for detailed logs
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    print("Starting Vehicle Loan Management System...")
    print("=" * 50)
    print("Test Credentials:")
    print("Admin: username='admin', password='admin123'")
    print("Agent: username='ramesh_k', password='admin123'")
    print("Customer: username='aarav_sharma', password='admin123'")
    print("=" * 50)
    
    try:
        app = LoginWindow()
        app.run()
    except Exception as e:
        logging.error(f"Application failed to start: {e}", exc_info=True)
        print(f"Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
