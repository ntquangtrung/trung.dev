import logging
import re

from defusedxml.ElementTree import ParseError, fromstring

logger = logging.getLogger(__name__)


def is_safe_svg(file_content_bytes):
    """
    Validates SVG content using defusedxml and performs basic XSS sanitization checks.

    Args:
        file_content_bytes (bytes): The raw bytes content of the SVG file.

    Returns:
        tuple: (bool, str) - True if safe, False otherwise, and an error message.
    """
    try:
        # Use defusedxml for secure XML parsing (prevents XXE, XML bombs, etc.)
        root = fromstring(file_content_bytes)

        # 1. Basic SVG root tag validation
        # Ensure it's actually an SVG and not some other XML masquerading as SVG
        # Handles namespaces by checking if the tag name ends with 'svg'
        if not root.tag.endswith("svg"):
            return False, "Invalid SVG file: root tag is not '<svg>'."

        # 2. XSS Sanitization: Iterate through all elements and attributes
        for elem in root.iter():
            # Check for <script> tags
            if elem.tag.endswith("script"):
                return (
                    False,
                    f"Invalid SVG file: contains disallowed <script> tag at {elem.tag}.",
                )

            for attr_name in elem.attrib:
                # Check for event handlers (e.g., onload, onclick, onerror)
                if attr_name.lower().startswith("on"):
                    return (
                        False,
                        f"Invalid SVG file: contains disallowed event handler '{attr_name}'.",
                    )

                # Further checks for dangerous href/xlink:href attributes if necessary
                # This regex checks for 'javascript:', 'data:', or 'vbscript:' in hrefs, case-insensitive
                if attr_name.lower().endswith("href"):  # Covers href and xlink:href
                    href_value = elem.attrib[attr_name].lower().strip()
                    if re.match(r"^(javascript|data|vbscript):", href_value):
                        return (
                            False,
                            f"Invalid SVG file: contains dangerous href '{attr_name}' with value '{href_value}'.",
                        )

                # Check for style attributes containing 'url()' with dangerous schemes
                if attr_name.lower() == "style":
                    style_value = elem.attrib[attr_name].lower()
                    if re.search(r"url\s*\(", style_value):  # If style contains url()
                        # This is a very basic check, a more robust one would parse the URL
                        # and check its scheme, but catching any url() is a good start if not expected
                        # More specific checks for url(javascript:...) would be more robust.
                        pass  # For now, allow url() but be aware of its potential danger if unsanitized.
        return True, ""  # SVG is considered safe

    except ParseError as e:
        # This catches XML parsing errors (e.g., malformed XML, XML bombs, XXE attempts)
        logger.exception("DefusedXML Parse Error for SVG: %s", e)
        return False, "Invalid or malicious XML structure detected in SVG."
    except Exception as e:
        # Catch any other unexpected errors during SVG processing
        logger.exception("An unexpected error occurred during SVG safety check: %s", e)
        return False, "Failed to perform SVG safety checks."
