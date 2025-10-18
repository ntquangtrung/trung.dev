import logging
import os
import uuid

from django.db import models
from django.core.files.base import ContentFile
from django.db.models.fields.files import ImageFieldFile

from utilities.convert_image_to_webp import convert_image_to_webp

logger = logging.getLogger(__name__)


class WebPImageFieldFile(ImageFieldFile):
    def save(self, name, content, save=True):
        webp_bytes, error = convert_image_to_webp(
            image_data=content.read(),
            quality=85,
            max_width=2048,
            max_height=2048,
        )

        if error:
            logger.error(f"Failed to convert {name} to WebP: {error}")
            raise ValueError(f"Image conversion failed: {error}")

        folder = os.path.dirname(name)
        unique_filename = f"{uuid.uuid4().hex}.webp"

        if folder:
            webp_name = os.path.join(folder, unique_filename)
        else:
            webp_name = unique_filename

        webp_content = ContentFile(webp_bytes)
        super().save(webp_name, webp_content, save)


class WebPImageField(models.ImageField):
    attr_class = WebPImageFieldFile
