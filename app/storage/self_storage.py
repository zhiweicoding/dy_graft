from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    def upload(self, file_path: str, key: str, meta_data: dict = None):
        pass
