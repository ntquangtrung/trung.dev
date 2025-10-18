import io
import logging

from PIL import Image

logger = logging.getLogger(__name__)


def convert_image_to_webp(
    image_data: bytes,
    quality: int = 85,
    max_width: int | None = None,
    max_height: int | None = None,
) -> tuple[bytes | None, str | None]:
    """
    Convert an image to WebP format using Pillow.

    Args:
        image_data: The raw bytes of the image to convert
        quality: WebP quality (1-100, default 85)
        max_width: Optional maximum width to resize to (maintains aspect ratio)
        max_height: Optional maximum height to resize to (maintains aspect ratio)

    Returns:
        A tuple of (webp_bytes, error_message).
        - If successful: (bytes, None)
        - If failed: (None, error_message_string)
    """
    try:
        # Validate quality parameter
        if not 1 <= quality <= 100:
            return None, f"Quality must be between 1 and 100, got {quality}"

        # Open the image from bytes
        image = Image.open(io.BytesIO(image_data))

        # Convert RGBA to RGB if necessary (WebP supports both, but RGB is more efficient)
        if image.mode in ("RGBA", "LA", "P"):
            # Create a white background for transparency
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(
                image, mask=image.split()[-1] if image.mode in ("RGBA", "LA") else None
            )
            image = background
        elif image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        # Resize if max dimensions are specified
        if max_width or max_height:
            original_width, original_height = image.size

            # Calculate new dimensions maintaining aspect ratio
            if max_width and max_height:
                ratio = min(max_width / original_width, max_height / original_height)
            elif max_width:
                ratio = max_width / original_width
            else:  # max_height only
                ratio = max_height / original_height

            # Only resize if image is larger than max dimensions
            if ratio < 1:
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                logger.info(
                    f"Resized image from {original_width}x{original_height} to {new_width}x{new_height}"
                )

        # Convert to WebP
        output = io.BytesIO()
        image.save(output, format="WEBP", quality=quality, method=6)
        webp_bytes = output.getvalue()

        logger.info(
            f"Successfully converted image to WebP (quality={quality}, size={len(webp_bytes)} bytes)"
        )
        return webp_bytes, None

    except Image.UnidentifiedImageError:
        error_msg = "Unable to identify image format. The file may be corrupted or not a valid image."
        logger.exception(error_msg)
        return None, error_msg

    except Image.DecompressionBombError:
        error_msg = "Image is too large and may be a decompression bomb attack."
        logger.exception(error_msg)
        return None, error_msg

    except OSError as e:
        error_msg = f"OS error while processing image: {e!s}"
        logger.exception(error_msg)
        return None, error_msg

    except MemoryError:
        error_msg = "Not enough memory to process the image."
        logger.exception(error_msg)
        return None, error_msg

    except Exception as e:
        error_msg = f"Unexpected error converting image to WebP: {e!s}"
        logger.exception(error_msg)
        return None, error_msg
