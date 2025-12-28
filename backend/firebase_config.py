import os
import json
import base64
import threading
from typing import Optional

import firebase_admin  # type: ignore
from firebase_admin import credentials, firestore  # type: ignore

# Module-level lock and cached clients to ensure Singleton behavior in multi-threaded FastAPI
_init_lock = threading.Lock()
_app_initialized = False
_db_client: Optional[firestore.Client] = None


def _load_credentials():
    """Resolve Firebase credentials from env or files."""
    # 1) Path from env
    path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if path:
        if not os.path.exists(path):
            raise FileNotFoundError(f"GOOGLE_APPLICATION_CREDENTIALS path not found: {path}")
        return credentials.Certificate(path)

    # 2) JSON content from env (raw or base64)
    raw = os.getenv("FIREBASE_CREDENTIALS_JSON")
    if raw:
        try:
            if raw.strip().startswith("{"):
                data = json.loads(raw)
            else:
                data = json.loads(base64.b64decode(raw).decode("utf-8"))
            return credentials.Certificate(data)
        except Exception as e:
            raise RuntimeError(f"Invalid FIREBASE_CREDENTIALS_JSON: {e}")

    # 3) Local files (project root, then backend/)
    for candidate in ("serviceAccountKey.json", os.path.join("backend", "serviceAccountKey.json")):
        if os.path.exists(candidate):
            # Validate JSON to surface empty/invalid files clearly
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    json.load(f)
            except Exception as e:
                raise RuntimeError(f"Invalid credentials file '{candidate}': {e}")
            return credentials.Certificate(candidate)

    raise FileNotFoundError(
        "No Firebase credentials found. Set GOOGLE_APPLICATION_CREDENTIALS, FIREBASE_CREDENTIALS_JSON, "
        "or place serviceAccountKey.json in project root or backend/."
    )


def _initialize_app() -> None:
    global _app_initialized
    if _app_initialized or firebase_admin._apps:
        _app_initialized = True
        return
    with _init_lock:
        if _app_initialized or firebase_admin._apps:
            _app_initialized = True
            return
        try:
            cred = _load_credentials()
            firebase_admin.initialize_app(cred)
            _app_initialized = True
        except Exception as e:
            # Defer raising to caller for better error reporting in API
            raise RuntimeError(f"Firebase initialization failed: {e}")


def get_db() -> firestore.Client:
    """
    Returns a Singleton Firestore client. Initializes the Firebase app on first call.
    Network hatalarını yakalar ve daha açıklayıcı hata mesajları verir.
    """
    global _db_client
    if _db_client is not None:
        return _db_client

    # Initialize app
    try:
        _initialize_app()
    except Exception as e:
        error_msg = str(e).lower()
        if "network" in error_msg or "connection" in error_msg or "timeout" in error_msg:
            raise RuntimeError(
                f"Firebase bağlantı hatası: İnternet bağlantınızı kontrol edin veya Firebase servisinin erişilebilir olduğundan emin olun. Detay: {e}"
            ) from e
        raise

    # Create client
    with _init_lock:
        if _db_client is None:
            try:
                _db_client = firestore.client()
            except Exception as e:
                error_msg = str(e).lower()
                if "network" in error_msg or "connection" in error_msg or "timeout" in error_msg:
                    raise RuntimeError(
                        f"Firestore client oluşturulamadı: Network hatası. İnternet bağlantınızı kontrol edin. Detay: {e}"
                    ) from e
                raise
    return _db_client
