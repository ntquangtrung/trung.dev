import os
import logging
from django.conf import settings
from django import template
from django.utils.safestring import mark_safe

register = template.Library()
logger = logging.getLogger(__name__)


@register.simple_tag
def render_svg(path, tailwind_css_color=""):
    """
    Renders an inline SVG file from the static directory with optional CSS color class.
    Example: {% render_svg "icons/anchor.svg" color="text-red-500" %}
    """
    full_path = os.path.join(settings.BASE_DIR, "static", path)
    try:
        with open(full_path, "r") as svg_file:
            svg_content = svg_file.read()
            if tailwind_css_color:
                # Add class to <svg> tag
                svg_content = svg_content.replace(
                    "<svg", f'<svg class="{tailwind_css_color}"', 1
                )
            return mark_safe(svg_content)
    except FileNotFoundError:
        logger.warning(f"SVG not found: {full_path}")
        return mark_safe(f"<!-- SVG not found: {path} -->")
    except Exception as e:
        logger.error(f"Error rendering SVG '{path}': {e}")
        return mark_safe(f"<!-- Error rendering SVG: {path} -->")
