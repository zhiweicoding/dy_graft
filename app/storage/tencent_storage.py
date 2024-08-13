# -*- coding=utf-8

import logging
import os
import sys
import json

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos.cos_exception import CosClientError, CosServiceError

from app.storage import self_storage


class TencentStorage(self_storage.Storage):

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
        self.secret_id = os.environ.get('COS_SECRET_ID', "default")
        self.secret_key = os.environ.get('COS_SECRET_KEY', "default")
        self.region = os.environ.get('COS_REGION', "ap-guangzhou")
        self.bucket_name: str = os.environ.get('COS_BUCKET', "default")
        self.domain: str = os.environ.get('COS_ENDPOINT', "default")
        self.token = None
        self.scheme = 'https'

        self.config = CosConfig(Region=self.region, SecretId=self.secret_id, SecretKey=self.secret_key,
                                Token=self.token, Scheme=self.scheme)
        self.client = CosS3Client(self.config)
        print("Installing Tencent cloud storage.")

    def upload(self, file_path: str, key: str, meta_data: dict = None):
        try:
            response = self.client.upload_file(
                Bucket=self.bucket_name,
                Key=key,
                LocalFilePath=file_path,
                Metadata=meta_data
            )
            print(f"File upload response: {json.dumps(response)}")
            return response
        except CosServiceError as e:
            print(e.get_error_code())
            print(e.get_error_msg())
            print(e.get_resource_location())
            return None
        except CosClientError as e:
            print(f'cos client error: {e}')
            return None
