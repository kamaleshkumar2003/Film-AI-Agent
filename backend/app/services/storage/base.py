from abc import ABC, abstractmethod

class BaseStorage(ABC):
    @abstractmethod
    async def save_file(self, file_bytes: bytes, filename: str) -> str:
        """Save bytes and return storage path."""
        pass

    @abstractmethod
    async def read_file(self, storage_path: str) -> bytes:
        """Read bytes from storage path."""
        pass
