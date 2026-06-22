import base64
import logging
import os
from io import BytesIO

import qrcode
import requests
from django.template.loader import get_template

from booking.models import Ticket

logger = logging.getLogger(__name__)

# Try to import weasyprint, fallback if C libraries are missing
try:
    import weasyprint
except (ImportError, OSError) as e:
    weasyprint = None
    logger.warning("WeasyPrint could not be loaded: %s. Will fall back to xhtml2pdf.", e)

# Try to import xhtml2pdf for fallback
try:
    from xhtml2pdf import pisa
except ImportError:
    pisa = None


def _build_qr_base64(ticket_code: str) -> str:
    img = qrcode.make(ticket_code)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def _build_event_image_base64(registration):
    event_image_base64 = None
    if not registration.event.image:
        return event_image_base64

    try:
        image_url = registration.event.image.url
        if image_url.startswith("//"):
            image_url = f"https:{image_url}"

        image_response = requests.get(image_url, timeout=10)
        if image_response.status_code == 200:
            event_image_base64 = base64.b64encode(
                image_response.content
            ).decode("utf-8")
    except Exception:
        logger.exception("Unable to fetch event image for ticket render")

    return event_image_base64


def build_ticket_html(registration, user):
    ticket = Ticket.objects.get(registration=registration)
    qr_image = _build_qr_base64(ticket.unique_code)
    event_image = _build_event_image_base64(registration)

    template = get_template("ticket.html")
    return template.render(
        {
            "user": user,
            "reg": registration,
            "qr_image": qr_image,
            "event_image": event_image,
        }
    )


def render_ticket_pdf_bytes(html: str) -> bytes:
    """Render ticket HTML to PDF using WeasyPrint (if available) or xhtml2pdf (fallback)."""
    if weasyprint is not None:
        try:
            return weasyprint.HTML(string=html).write_pdf()
        except Exception as e:
            logger.exception("WeasyPrint rendering failed, trying xhtml2pdf fallback: %s", e)

    if pisa is not None:
        result = BytesIO()
        pisa_status = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
        if not pisa_status.err:
            return result.getvalue()
        else:
            raise RuntimeError(f"xhtml2pdf rendering failed: {pisa_status.err}")

    raise RuntimeError("No PDF rendering engine available. Install WeasyPrint or xhtml2pdf.")


def generate_ticket_pdf_bytes(registration, user) -> bytes:
    html = build_ticket_html(registration, user)
    return render_ticket_pdf_bytes(html)
