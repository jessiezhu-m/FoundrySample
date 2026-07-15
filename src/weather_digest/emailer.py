from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from urllib.parse import quote

import requests
from azure.communication.email import EmailClient
from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)

GRAPH_SCOPE = "https://graph.microsoft.com/.default"
GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


def build_weather_email(sender: str, recipient: str, body: str) -> EmailMessage:
    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = "Shanghai Weather and Travel Advice"
    message.set_content(body)
    return message


class SmtpEmailSender:
    def __init__(self, host: str, port: int, username: str, password: str) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password

    def send(self, message: EmailMessage) -> None:
        with smtplib.SMTP(self._host, self._port, timeout=30) as smtp:
            smtp.starttls()
            smtp.login(self._username, self._password)
            smtp.send_message(message)


class GraphEmailSender:
    """Send mail through the Microsoft Graph API using Azure AD (modern auth).

    Uses ``DefaultAzureCredential`` (e.g. your ``az login`` session), so no SMTP
    username/password is needed. This avoids the "basic authentication is
    disabled" error returned by Office 365 SMTP.
    """

    def __init__(
        self,
        credential: TokenCredential | None = None,
        sender: str | None = None,
    ) -> None:
        self._credential = credential or DefaultAzureCredential(
            exclude_interactive_browser_credential=False
        )
        self._sender = sender

    def send(self, message: EmailMessage) -> None:
        token = self._credential.get_token(GRAPH_SCOPE).token
        payload = _email_message_to_graph_payload(message)

        if self._sender:
            url = f"{GRAPH_BASE_URL}/users/{quote(self._sender, safe='')}/sendMail"
        else:
            url = f"{GRAPH_BASE_URL}/me/sendMail"

        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )

        if response.status_code >= 400:
            raise RuntimeError(
                "Microsoft Graph sendMail failed "
                f"({response.status_code}): {response.text}"
            )

        logger.info("Email sent via Microsoft Graph (status %s).", response.status_code)


def _email_message_to_graph_payload(message: EmailMessage) -> dict:
    recipients = [addr.strip() for addr in message["To"].split(",") if addr.strip()]
    return {
        "message": {
            "subject": message["Subject"],
            "body": {
                "contentType": "Text",
                "content": message.get_content(),
            },
            "toRecipients": [
                {"emailAddress": {"address": address}} for address in recipients
            ],
        },
        "saveToSentItems": True,
    }


class AcsEmailSender:
    """Send mail through Azure Communication Services (ACS) Email.

    ACS does not depend on an Office 365 mailbox identity, so it avoids the
    SMTP "basic authentication is disabled" and Graph 403/404 errors. The
    ``sender`` address must belong to a domain provisioned in your ACS Email
    resource (for example ``DoNotReply@<guid>.azurecomm.net``).
    """

    def __init__(self, connection_string: str) -> None:
        self._client = EmailClient.from_connection_string(connection_string)

    def send(self, message: EmailMessage) -> None:
        recipients = [
            addr.strip() for addr in message["To"].split(",") if addr.strip()
        ]
        email_message = {
            "senderAddress": message["From"],
            "content": {
                "subject": message["Subject"],
                "plainText": message.get_content(),
            },
            "recipients": {
                "to": [{"address": address} for address in recipients],
            },
        }

        poller = self._client.begin_send(email_message)
        result = poller.result()
        logger.info("Email sent via ACS (status %s).", result["status"])

