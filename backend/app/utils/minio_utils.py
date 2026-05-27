from minio import Minio
from app.config import settings
import io
import os
from pathlib import Path

class MinioStorage:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket()

    def _ensure_bucket(self):
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
            # 设置存储桶策略为公共读取（如果是生产环境建议使用预签名URL）
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                        "Resource": [f"arn:aws:s3:::{self.bucket_name}"]
                    },
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"]
                    }
                ]
            }
            import json
            self.client.set_bucket_policy(self.bucket_name, json.dumps(policy))

    async def upload_file(self, file_data: bytes, object_name: str, content_type: str = "application/octet-stream"):
        """上传字节流到 MinIO"""
        data_stream = io.BytesIO(file_data)
        self.client.put_object(
            self.bucket_name,
            object_name,
            data_stream,
            length=len(file_data),
            content_type=content_type
        )
        return self.get_url(object_name)

    def upload_local_file(self, local_path: str, object_name: str):
        """上传本地文件到 MinIO"""
        self.client.fput_object(self.bucket_name, object_name, local_path)
        return self.get_url(object_name)

    def get_url(self, object_name: str):
        """获取对象访问 URL（浏览器端使用 PUBLIC_ENDPOINT）"""
        endpoint = settings.MINIO_PUBLIC_ENDPOINT or settings.MINIO_ENDPOINT
        protocol = "https" if settings.MINIO_SECURE else "http"
        return f"{protocol}://{endpoint}/{self.bucket_name}/{object_name}"

storage = MinioStorage()
