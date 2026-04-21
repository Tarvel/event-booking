import logging
import threading

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from booking.models import Registration
from events.utils.ticket_pdf import generate_ticket_pdf_bytes

logger = logging.getLogger(__name__)


def _send_email(
    subject: str,
    to_email: str,
    html_template: str,
    context: dict,
    attachments=None,
) -> bool:
    """Handles rendering and sending HTML + text email."""
    try:
        html_content = render_to_string(html_template, context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=subject.title(),
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        email.attach_alternative(html_content, "text/html")

        # Attach files (if any)
        if attachments:
            for filename, content, mimetype in attachments:
                email.attach(filename, content, mimetype)

        email.send(fail_silently=False)
        logger.info("Email '%s' sent to %s", subject, to_email)
        return True

    except Exception as exc:
        logger.exception(
            "Failed to send email '%s' to %s: %s",
            subject,
            to_email,
            exc,
        )
        return False


def send_ticket_email(to_email: str, name: str, ticket_name: str) -> bool:
    """Send simple ticket notification email."""
    context = {
        "current_date": timezone.now(),
        "name": name,
        "ticket_name": ticket_name,
    }
    return _send_email(
        "Your Ticket Has Arrived!",
        to_email,
        "emails/ticket_email.html",
        context,
    )


def send_ticket_email_async(to_email, name, ticket_name):
    threading.Thread(
        target=send_ticket_email,
        args=(to_email, name, ticket_name),
        daemon=True,
    ).start()


def send_ticket_email_with_pdf(slug, user):
    """Generate PDF ticket and send via email."""
    try:
        reg = (
            Registration.objects.filter(
                event__slug=slug,
                user=user,
                status="approved",
            )
            .select_related("event")
            .first()
        )
        if not reg:
            logger.warning(
                "No registration found for slug '%s' and user '%s'",
                slug,
                user.email,
            )
            return False

        pdf_bytes = generate_ticket_pdf_bytes(registration=reg, user=user)

        filename = f"{reg.event.title.title()}_Ticket_For_{user.email}.pdf"

        # Send email with attachment using _send_email
        context = {
            "name": user.get_full_name(),
            "event": reg.event.title,
            "date": timezone.now(),
        }

        return _send_email(
            subject="Your Event Ticket",
            to_email=user.email,
            html_template="emails/ticket_email.html",
            context=context,
            attachments=[(filename, pdf_bytes, "application/pdf")],
        )

    except Exception as exc:
        logger.exception(
            "Failed to send ticket email with PDF to %s: %s", user.email, exc
        )
        return False


def send_ticket_email_with_pdf_async(slug, user):
    """Send ticket email with PDF asynchronously."""
    threading.Thread(
        target=send_ticket_email_with_pdf,
        args=(slug, user),
        daemon=True,
    ).start()
