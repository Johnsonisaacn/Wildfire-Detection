# diagnose_imports.py
import sys
import email.mime
import email.mime.multipart

print("Python version:", sys.version)
print("\nTrying to import MimeMultipart...")

try:
    from email.mime.multipart import MimeMultipart
    print("✅ SUCCESS: MimeMultipart imported successfully")
    print("MimeMultipart class:", MimeMultipart)
except ImportError as e:
    print("❌ FAILED: Could not import MimeMultipart")
    print("Error:", e)
    print("\nAvailable in email.mime.multipart:")
    print(dir(email.mime.multipart))

print("\nTrying alternative import...")
try:
    import email.mime.multipart as multipart
    MimeMultipart = multipart.MimeMultipart
    print("✅ SUCCESS: MimeMultipart accessed via alternative method")
except Exception as e:
    print("❌ FAILED: Alternative import also failed")
    print("Error:", e)

print("\nEmail package location:", email.__file__)