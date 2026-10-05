import pytest

from okpop import mail


def test_send_mail(monkeypatch):
    sent_messages = []

    class FakeSMTP:
        def __init__(self, host, port):
            assert host == "smtp.gmail.com"
            assert port == 465

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            pass

        def login(self, address, password):
            assert address == "test@gmail.com"
            assert password == "test-password"

        def send_message(self, msg):
            sent_messages.append(msg)

    monkeypatch.setenv(
        "OKPOP_GMAIL_ADDRESS",
        "test@gmail.com",
    )

    monkeypatch.setenv(
        "OKPOP_GMAIL_APP_PASSWORD",
        "test-password",
    )

    monkeypatch.setattr(
        mail.smtplib,
        "SMTP_SSL",
        FakeSMTP,
    )

    mail.send_mail(
        to_address="receiver@example.com",
        subject="OKPOP test",
        body="test message",
    )

    assert len(sent_messages) == 1

    msg = sent_messages[0]

    assert msg["From"] == "test@gmail.com"
    assert msg["To"] == "receiver@example.com"
    assert msg["Subject"] == "OKPOP test"
    assert msg.get_content().strip() == "test message"

    assert list(msg.iter_attachments()) == []


def test_send_mail_with_attachment(
    monkeypatch,
    tmp_path,
):
    sent_messages = []

    class FakeSMTP:
        def __init__(self, host, port):
            pass

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            pass

        def login(self, address, password):
            pass

        def send_message(self, msg):
            sent_messages.append(msg)

    monkeypatch.setenv(
        "OKPOP_GMAIL_ADDRESS",
        "test@gmail.com",
    )

    monkeypatch.setenv(
        "OKPOP_GMAIL_APP_PASSWORD",
        "test-password",
    )

    monkeypatch.setattr(
        mail.smtplib,
        "SMTP_SSL",
        FakeSMTP,
    )

    attachment = tmp_path / "report.zip"

    attachment.write_bytes(
        b"test zip data"
    )

    mail.send_mail(
        to_address="receiver@example.com",
        subject="OKPOP report",
        body="report attached",
        attachment=attachment,
    )

    msg = sent_messages[0]

    attachments = list(
        msg.iter_attachments()
    )

    assert len(attachments) == 1

    attached = attachments[0]

    assert attached.get_filename() == "report.zip"
    assert attached.get_content() == b"test zip data"

def test_send_mail_without_gmail_address(
    monkeypatch,
):
    monkeypatch.delenv(
        "OKPOP_GMAIL_ADDRESS",
        raising=False,
    )

    monkeypatch.setenv(
        "OKPOP_GMAIL_APP_PASSWORD",
        "test-password",
    )

    with pytest.raises(KeyError):
        mail.send_mail(
            to_address="receiver@example.com",
            subject="OKPOP test",
            body="test message",
        )


def test_send_mail_without_app_password(
    monkeypatch,
):
    monkeypatch.setenv(
        "OKPOP_GMAIL_ADDRESS",
        "test@gmail.com",
    )

    monkeypatch.delenv(
        "OKPOP_GMAIL_APP_PASSWORD",
        raising=False,
    )

    with pytest.raises(KeyError):
        mail.send_mail(
            to_address="receiver@example.com",
            subject="OKPOP test",
            body="test message",
        )


