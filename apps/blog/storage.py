import logging

import requests
from django.core.files.base import ContentFile
from django.core.files.storage import Storage

from services.seaweedfs import SeaweedFSClient

logger = logging.getLogger(__name__)


class SeaweedStorage(Storage):
    """
    Custom Django Storage backend using SeaweedFS filer API.
    """

    def __init__(self, base_url=None, prefix=None):
        self.base_url = base_url
        self.prefix = prefix

        if not self.base_url or not self.prefix:
            logger.error(
                "SeaweedFS configuration missing",
                extra={"base_url": base_url, "prefix": prefix},
            )
            raise ValueError(
                "SEAWEEDFS_URL and SEAWEEDFS_PREFIX are required in settings."
            )

        self.client = SeaweedFSClient(self.base_url)
        logger.info(
            "SeaweedStorage initialized", extra={"base_url": base_url, "prefix": prefix}
        )

    def _save(self, name, content):
        """
        Save file to SeaweedFS.
        """
        full_path = f"{self.prefix}/{name}"

        try:
            file_size = (
                content.size if hasattr(content, "size") else len(content.read())
            )
            content.seek(0)  # Reset file pointer after reading size

            file_data = content.read()
            self.client.upload_file(full_path, file_data)

            logger.info(
                "File saved to SeaweedFS",
                extra={
                    "file_path": full_path,
                    "file_name": name,
                    "file_size": file_size,
                },
            )
            return full_path
        except Exception as e:
            logger.exception(
                "Failed to save file to SeaweedFS",
                extra={
                    "file_path": full_path,
                    "file_name": name,
                    "error": str(e),
                },
            )
            raise

    def _open(self, name, _mode="rb"):
        """
        Retrieve file from SeaweedFS.
        """
        try:
            file_bytes = self.client.get_file(name)
            logger.info(
                "File retrieved from SeaweedFS",
                extra={"file_path": name, "size": len(file_bytes)},
            )
            return ContentFile(file_bytes)
        except Exception as e:
            logger.exception(
                "Failed to retrieve file from SeaweedFS",
                extra={"file_path": name, "error": str(e)},
            )
            raise

    def delete(self, name):
        try:
            self.client.delete_file(name)
            logger.info("File deleted from SeaweedFS", extra={"file_path": name})
        except Exception as e:
            logger.exception(
                "Failed to delete file from SeaweedFS",
                extra={"file_path": name, "error": str(e)},
            )
            raise

    def exists(self, name):
        """
        Check if file exists via HEAD request.
        """
        try:
            url = f"{self.base_url}/{name}"
            response = requests.head(url, timeout=5)
            exists = response.status_code == 200

            logger.debug(
                "File existence check",
                extra={
                    "file_path": name,
                    "exists": exists,
                    "status_code": response.status_code,
                },
            )
            return exists
        except requests.RequestException as e:
            logger.warning(
                "Failed to check file existence",
                extra={"file_path": name, "error": str(e)},
            )
            return False

    def url(self, name):
        """
        Return public URL.
        """
        return self.client.get_file_url(name)
