import logging
from urllib.parse import quote

from ..config import settings

log = logging.getLogger(__name__)


def send_reset_link(email: str, token: str) -> None:
    # Link is built from the configured origin, never from the request's Host header.
    link = f"{settings.web_origin}/reset?token={quote(token, safe='')}"
    _deliver(to=email, subject="Reset your password", body=f"Use this link within one hour: {link}")


def _deliver(to: str, subject: str, body: str) -> None:
    # Transport lives in the mail worker; this stub only logs the delivery request id.
    log.info("queued mail to=%s subject=%s", to, subject)
