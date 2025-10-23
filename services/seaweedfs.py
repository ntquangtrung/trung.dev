from urllib.parse import urljoin

import requests
from django.conf import settings


class SeaweedFSClient:
    """
    A minimal REST client for SeaweedFS filer API.
    """

    def __init__(self, base_url: str):
        # base_url example: http://seaweedfs-filer:8888
        self.base_url = base_url.rstrip("/")

    def upload_file(self, file_path: str, file_data: bytes):
        """
        Upload file_data (bytes or file object) to SeaweedFS under file_path.
        Example file_path: "uploads/myfile.png"
        """
        url = urljoin(f"{self.base_url}/", file_path)
        files = {"file": (file_path, file_data)}
        response = requests.post(url, files=files)
        response.raise_for_status()
        return response.json()

    def get_file(self, file_path: str):
        """
        Retrieve a file's content as bytes.
        """
        url = urljoin(f"{self.base_url}/", file_path)
        response = requests.get(url)
        response.raise_for_status()
        return response.content

    def delete_file(self, file_path: str):
        """
        Delete file from SeaweedFS.
        """
        url = urljoin(f"{self.base_url}/", file_path)
        response = requests.delete(url)
        response.raise_for_status()
        return True

    def get_file_url(self, file_path: str):
        """
        Return an accessible public URL (if filer port is exposed).
        On production, we need to return relative path and let nginx handle the file.
        """

        if settings.DEBUG:
            return f"{self.base_url}/{file_path}"
        return f"/{file_path}"
