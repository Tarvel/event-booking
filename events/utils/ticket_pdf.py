import base64
import logging
import os
from io import BytesIO

import qrcode
import requests
import weasyprint
from django.template.loader import get_template

from booking.models import Ticket

logger = logging.getLogger(__name__)


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
    """Render ticket HTML to PDF using WeasyPrint.

    WeasyPrint uses Cairo/Pango for rendering, which supports modern CSS
    including gradients, table-cell layout, border-radius, and base64
    images — producing output near-identical to a web browser.
    """
    return weasyprint.HTML(string=html).write_pdf()


def generate_ticket_pdf_bytes(registration, user) -> bytes:
    html = build_ticket_html(registration, user)
    return render_ticket_pdf_bytes(html)
