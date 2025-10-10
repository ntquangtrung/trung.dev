from django.conf import settings
from django.http import HttpResponse, Http404
import requests


def serve_seaweedfs_file(request, path):
    # Construct SeaweedFS filer URL
    filer_url = (
        f"{settings.SEAWEEDFS_URL}/{settings.SEAWEEDFS_PREFIX}/{path.rstrip('/')}"
    )
    resp = requests.get(filer_url, stream=True)

    if resp.status_code != 200:
        raise Http404("File not found in SeaweedFS")

    content_type = resp.headers.get("Content-Type", "application/octet-stream")
    return HttpResponse(resp.content, content_type=content_type)
