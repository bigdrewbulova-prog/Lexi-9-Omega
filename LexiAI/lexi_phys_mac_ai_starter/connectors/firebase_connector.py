import os

def init_firebase():
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        raise RuntimeError("Missing GOOGLE_APPLICATION_CREDENTIALS in .env")
    import firebase_admin
    from firebase_admin import credentials
    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.Certificate(cred_path))
    return firebase_admin
