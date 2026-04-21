import re
from django import template

register = template.Library()


@register.simple_tag
def cloud_thumb(image, width=400, height=300):
    """
    Rewrite a Cloudinary URL to include resize/optimize transformations.
    Usage: {% cloud_thumb event.image 400 300 %}
    Returns the transformed URL string, or empty string if no image.
    """
    if not image:
        return ""

    try:
        url = image.url
    except Exception:
        url = str(image)

    # Handle protocol-relative URLs
    if url.startswith("//"):
        url = "https:" + url

    # Insert transformation before the version/public_id segment
    # Cloudinary URLs look like: .../image/upload/v1234567890/public_id.jpg
    # We want: .../image/upload/c_fill,w_400,h_300,q_auto,f_auto/v1234567890/public_id.jpg
    transform = f"c_fill,w_{width},h_{height},q_auto,f_auto"

    pattern = r"(/image/upload/)"
    replacement = rf"\1{transform}/"
    transformed = re.sub(pattern, replacement, url)

    return transformed
