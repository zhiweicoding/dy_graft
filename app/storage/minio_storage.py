# -*- coding=utf-8

import logging
import os
import sys

from minio import Minio
from minio.error import S3Error

from app.storage import self_storage


class MinioStorage(self_storage.Storage):

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
        self.access_key = os.environ.get('MINIO_ACCESS_KEY', "default")
        self.secret_key = os.environ.get('MINIO_SECRET_KEY', "default")
        self.bucket_name: str = os.environ.get('MINIO_BUCKET', "default")
        self.endpoint: str = os.environ.get('MINIO_ENDPOINT', "http://localhost:9000")
        self.secure = os.environ.get('MINIO_SECURE', 'false').lower() == 'true'

        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )
        print("Installing MinIO storage.")

    def upload(self, file_path: str, key: str, meta_data: dict = None):
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)

            response = self.client.fput_object(
                bucket_name=self.bucket_name,
                object_name=key,
                file_path=file_path,
                metadata=meta_data
            )
            print(f"File upload response: {str(response)}")
            return response
        except S3Error as e:
            print(f'MinIO S3 error: {e}')
            return None
