from app.storage.tencent_storage import TencentStorage
from app.storage.minio_storage import MinioStorage


def get_storage(storage_type):
    if storage_type == 'tencent':
        tencentStorage = TencentStorage()
        return tencentStorage
    if storage_type == 'minio':
        minioStorage = MinioStorage()
        return minioStorage
    else:
        raise ValueError("Unknown storage type")
