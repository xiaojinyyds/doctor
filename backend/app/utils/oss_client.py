#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""OSS client with local file fallback for demo environments."""

from datetime import datetime
import logging
from pathlib import Path
import uuid

import oss2

from app.core.config import settings

logger = logging.getLogger(__name__)


class OSSClient:
    """Upload files to OSS when configured, otherwise store them locally."""

    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        self.bucket = None
        self.use_oss = bool(
            settings.OSS_ACCESS_KEY.strip()
            and settings.OSS_SECRET_KEY.strip()
            and settings.OSS_ENDPOINT.strip()
            and settings.OSS_BUCKET_NAME.strip()
        )

        if self.use_oss:
            auth = oss2.Auth(
                settings.OSS_ACCESS_KEY.strip(),
                settings.OSS_SECRET_KEY.strip(),
            )
            self.bucket = oss2.Bucket(
                auth,
                settings.OSS_ENDPOINT.strip(),
                settings.OSS_BUCKET_NAME.strip(),
            )
        else:
            logger.warning("OSS config missing, using local upload storage")

        if settings.OSS_DOMAIN:
            self.domain = settings.OSS_DOMAIN.rstrip("/")
        else:
            self.domain = f"https://{settings.OSS_BUCKET_NAME}.{settings.OSS_ENDPOINT}".rstrip(".")

    def upload_file(self, file_content: bytes, filename: str, folder: str = "medical-images") -> dict:
        file_ext = Path(filename or "").suffix.lower()
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        object_key = f"{folder}/{datetime.now().strftime('%Y%m%d')}/{unique_filename}"

        if self.use_oss and self.bucket is not None:
            try:
                result = self.bucket.put_object(object_key, file_content)
                if result.status != 200:
                    raise RuntimeError(f"upload failed: {result.status}")

                return {
                    "url": f"{self.domain}/{object_key}",
                    "key": object_key,
                    "size": len(file_content),
                    "storage": "oss",
                }
            except Exception as e:
                logger.warning("OSS upload failed, falling back to local storage: %s", e)

        local_path = self.upload_dir / Path(object_key)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(file_content)

        return {
            "url": f"{settings.BACKEND_URL.rstrip('/')}/uploads/{object_key}",
            "key": object_key,
            "size": len(file_content),
            "storage": "local",
        }

    def delete_file(self, object_key: str) -> bool:
        try:
            if self.use_oss and self.bucket is not None:
                result = self.bucket.delete_object(object_key)
                return result.status == 204

            local_path = self.upload_dir / Path(object_key)
            if local_path.exists():
                local_path.unlink()
            return True
        except Exception as e:
            logger.warning("Delete file failed: %s", e)
            return False

    def get_file_url(self, object_key: str, expires: int = 3600) -> str:
        if self.use_oss and self.bucket is not None:
            return self.bucket.sign_url("GET", object_key, expires)
        return f"{settings.BACKEND_URL.rstrip('/')}/uploads/{object_key}"

    def download_file(self, object_key: str) -> bytes:
        if self.use_oss and self.bucket is not None:
            result = self.bucket.get_object(object_key)
            return result.read()
        return (self.upload_dir / Path(object_key)).read_bytes()


oss_client = OSSClient()
