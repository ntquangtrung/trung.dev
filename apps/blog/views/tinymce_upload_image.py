import uuid
import os

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.utils.text import get_valid_filename
from django.conf import settings

from utilities.defused_svg import is_safe_svg
from utilities.convert_image_to_webp import convert_image_to_webp


def tinymce_upload_image(request):
    if request.method == "POST" and request.FILES.get("file"):
        image = request.FILES["file"]

        valid_mime_types = [
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "image/svg+xml",
        ]
        if image.content_type not in valid_mime_types:
            return JsonResponse({"error": "Unsupported file type."}, status=400)

        max_size = settings.MAX_UPLOAD_SIZE
        if image.size > max_size:
            return JsonResponse({"error": "File too large."}, status=400)

        ext = os.path.splitext(image.name)[1]

        # Special handling for SVG
        if image.content_type == "image/svg+xml" or ext.lower() == ".svg":
            svg_bytes = image.read()
            is_safe, error_msg = is_safe_svg(svg_bytes)
            if not is_safe:
                return JsonResponse({"error": error_msg}, status=400)
            unique_name = f"{uuid.uuid4()}{ext}"
            safe_name = get_valid_filename(unique_name)
            path = default_storage.save(
                f"{settings.DEFAULT_UPLOAD_PREFIX}{safe_name}", ContentFile(svg_bytes)
            )
        else:
            # Convert other images to WebP
            image_bytes = image.read()
            webp_bytes, error_msg = convert_image_to_webp(
                image_bytes, quality=85, max_width=2048, max_height=2048
            )

            if error_msg:
                return JsonResponse(
                    {"error": f"Image conversion failed: {error_msg}"}, status=400
                )

            unique_name = f"{uuid.uuid4().hex}.webp"
            safe_name = get_valid_filename(unique_name)
            path = default_storage.save(
                f"{settings.DEFAULT_UPLOAD_PREFIX}{safe_name}", ContentFile(webp_bytes)
            )

        return JsonResponse({"location": f"/{path}"})
    return JsonResponse({"error": "Invalid request"}, status=400)
