from app.storage.tencent_storage import TencentStorage


def get_storage(storage_type):
    if storage_type == 'tencent':
        tencentStorage = TencentStorage()
        return tencentStorage
    else:
        raise ValueError("Unknown storage type")
