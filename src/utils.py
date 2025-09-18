import os
import uuid
from typing import Optional
from pathlib import Path

# Optional DB imports only used by ensure_unique_source_id()
try:
    from src.db import SessionLocal , Source
except Exception:
    SessionLocal = None
    Source = None

DEFAULT_STORAGE_DIR = "storage"
DEFAULT_ID_LENGTH = None  # None => full uuid4 hex (recommended). Set int to shorten.

def generate_source_id(length: Optional[int] = DEFAULT_ID_LENGTH) -> str:
    """
    Generate a uuid4-based source id.
    - length=None -> full uuid4().hex (32 chars)
    - length=int -> first `length` hex chars (e.g., 8)
    """
    sid = uuid.uuid4().hex
    if length is None:
        return sid
    if length <= 0:
        raise ValueError("length must be positive or None")
    return sid[:length]

def ensure_unique_source_id(db_session=None, length: Optional[int] = DEFAULT_ID_LENGTH, max_attempts: int = 8) -> str:
    """
    Generate an id and (optionally) ensure it's not already in the DB.
    - If db_session is provided, it must be an active SQLAlchemy session.
    - If no db_session provided, returns generate_source_id(length).
    """
    if db_session is None or Source is None:
        # No DB check available; return single generated id
        return generate_source_id(length)

    attempts = 0
    while attempts < max_attempts:
        sid = generate_source_id(length)
        exists = db_session.query(Source).filter_by(source_id=sid).first()
        if not exists:
            return sid
        attempts += 1
    raise RuntimeError(f"Failed to generate unique source_id after {max_attempts} attempts")

def is_pdf_bytes(b: bytes) -> bool:
    """
    Quick check whether bytes look like a PDF (starts with %PDF-).
    Not bulletproof but good early validation.
    """
    if not b or len(b) < 4:
        return False
    try:
        return b.startswith(b"%PDF-")
    except Exception:
        return False

def get_storage_path(source_id: str, storage_dir: str = DEFAULT_STORAGE_DIR) -> str:
    Path(storage_dir).mkdir(parents=True, exist_ok=True)
    return os.path.join(storage_dir, f"{source_id}.pdf")

def save_pdf_bytes(file_bytes: bytes, source_id: str, storage_dir: str = DEFAULT_STORAGE_DIR) -> str:
    """
    Save raw bytes to storage/{source_id}.pdf. Returns the written path.
    """
    path = get_storage_path(source_id, storage_dir=storage_dir)
    with open(path, "wb") as f:
        f.write(file_bytes)
    return path
