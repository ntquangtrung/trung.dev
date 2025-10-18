import requests
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from services.seaweedfs import SeaweedFSClient


class SeaweedStorage(Storage):
    """
    Custom Django Storage backend using SeaweedFS filer API.
    """

    def __init__(self, base_url=None, prefix=None):
        self.base_url = base_url
        self.prefix = prefix

        if not self.base_url or not self.prefix:
            raise ValueError(
                "SEAWEEDFS_URL and SEAWEEDFS_PREFIX are required in settings."
            )

        self.client = SeaweedFSClient(self.base_url)

    def _save(self, name, content):
        """
        Save file to SeaweedFS.
        """
        name = f"{self.prefix}/{name}"
        file_data = content.read()
        self.client.upload_file(name, file_data)
        return name

    def _open(self, name, mode="rb"):
        """
        Retrieve file from SeaweedFS.
        """
        file_bytes = self.client.get_file(name)
        return ContentFile(file_bytes)

    def delete(self, name):
        self.client.delete_file(name)

    def exists(self, name):
        """
        You could check if file exists via HEAD request.
        """
        try:
            url = f"{self.base_url}/{name}"
            response = requests.head(url)
            return response.status_code == 200
        except Exception:
            return False

    def url(self, name):
        """
        Return public URL.
        """
        return self.client.get_file_url(name)
