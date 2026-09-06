import os
import uuid
from pathlib import Path
from app.services.storage.base import BaseStorage
from app.config import settings

class LocalStorage(BaseStorage):
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir or settings.STORAGE_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(self, file_bytes: bytes, filename: str) -> str:
        ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4()}{ext}"
        target_path = self.base_dir / unique_name
        
        # Write bytes
        with open(target_path, "wb") as f:
            f.write(file_bytes)
            
        return str(target_path.resolve())

    async def read_file(self, storage_path: str) -> bytes:
        p = Path(storage_path)
        if not p.exists():
            raise FileNotFoundError(f"Stored file not found at {storage_path}")
        with open(p, "rb") as f:
            return f.read()

storage_service = LocalStorage()
