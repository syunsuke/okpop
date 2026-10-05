import os
import smtplib
from email.message import EmailMessage
from pathlib import Path


def send_mail(
    to_address: str,
    subject: str,
    body: str,
    attachment: str | Path | None = None
) -> None:
    """Gmailを使ってメールを送信する。"""

    gmail_address = os.environ[
        "OKPOP_GMAIL_ADDRESS"
    ]
    app_password = os.environ[
        "OKPOP_GMAIL_APP_PASSWORD"
    ]

    msg = EmailMessage()

    msg["From"] = gmail_address
    msg["To"] = to_address
    msg["Subject"] = subject

    msg.set_content(body)

    if attachment is not None:
        attachment = Path(attachment)

        with attachment.open("rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="zip",
                filename=attachment.name,
            )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
    ) as smtp:
        smtp.login(
            gmail_address,
            app_password,
        )
        smtp.send_message(msg)
