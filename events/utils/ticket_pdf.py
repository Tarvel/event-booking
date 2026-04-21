import base64
import logging
import os
import shutil
from io import BytesIO

import qrcode
import requests
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
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright is not installed. Install dependencies and run "
            "'python -m playwright install chromium'."
        ) from exc

    def resolve_chromium_executable() -> str | None:
        env_path = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH")
        if env_path and os.path.exists(env_path):
            return env_path

        for candidate in (
            "chromium",
            "chromium-browser",
            "google-chrome",
            "google-chrome-stable",
        ):
            path = shutil.which(candidate)
            if path:
                return path

        return None

    with sync_playwright() as p:
        launch_kwargs = {
            "headless": True,
            "args": ["--no-sandbox", "--disable-dev-shm-usage"],
        }
        browser_path = resolve_chromium_executable()
        if browser_path:
            launch_kwargs["executable_path"] = browser_path

        try:
            browser = p.chromium.launch(**launch_kwargs)
        except PlaywrightError as exc:
            if "Executable doesn't exist" in str(exc):
                raise RuntimeError(
                    "Chromium browser binary not found. "
                    "Run 'python -m playwright install chromium' "
                    "or set PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH."
                ) from exc
            raise

        page = browser.new_page(viewport={"width": 1120, "height": 780})
        page.set_content(html, wait_until="networkidle")
        pdf_bytes = page.pdf(
            print_background=True,
            width="210mm",
            height="148mm",
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            prefer_css_page_size=True,
        )
        browser.close()

    return pdf_bytes


def generate_ticket_pdf_bytes(registration, user) -> bytes:
    html = build_ticket_html(registration, user)
    return render_ticket_pdf_bytes(html)
