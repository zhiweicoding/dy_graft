# -*- coding=utf-8
import json
import os

from fastapi import APIRouter
from app.entity.base_response import BaseResponse
import uuid
import requests
import tempfile
from app.entity.base_receive import UploadReceive
from app.storage import storage_factory

router = APIRouter()

cdn_url = os.environ['CDN_URL']


@router.post("/", response_model=BaseResponse)
async def init(upload_entity: UploadReceive):
    temp_path: str = download_file_to_temp(upload_entity.download_url, upload_entity.suffix)
    uuid_str: str = str(uuid.uuid1())
    print(f"temp_path: {temp_path}")
    storage_type = os.environ.get('STORAGE_TYPE', 'default')
    storage = storage_factory.get_storage(storage_type)
    upload_response = storage.upload(temp_path, uuid_str + '.' + upload_entity.suffix,
                                     meta_data=dict(cell_id=upload_entity.cell_id))

    print(f"upload_response:{json.dumps(upload_response)}")

    return BaseResponse(code=200, message="success",
                        data=dict(url=cdn_url + uuid_str + "." + upload_entity.suffix)).json()


def download_file_to_temp(url: str, suffix: str):
    # 使用 requests 获取文件数据
    response = requests.get(url, stream=True)

    # 检查请求是否成功
    if response.status_code == 200:
        # 使用 tempfile 创建一个临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.' + suffix) as tmp_file:
            # 写入数据到临时文件
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # 过滤掉保持连接的新块
                    tmp_file.write(chunk)
            # 返回临时文件的路径
            return tmp_file.name
    else:
        print(f"Failed to download: status code {response.status_code}")
        return None
