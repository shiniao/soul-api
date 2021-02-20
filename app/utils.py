from datetime import timedelta, datetime
from typing import Union, Any

import bcrypt
import emails
import jwt
from emails.template import JinjaTemplate as T
from loguru import logger

from app.config import settings


# security

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    generate jwt token
    :param subject: subject need to save in token
    :param expires_delta: expires time
    :return: token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def get_hashed_password(password: str) -> str:
    return bcrypt.hashpw(password, bcrypt.gensalt())


def verify_password(origin_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(origin_password, hashed_password)


# email

def send_email(
        email_to: str,
        subject_template: str = "",
        html_template: str = "",
        environment=None,
) -> None:
    """
    send email to some mail address
    :param email_to: send to this email
    :param subject_template: email subject
    :param html_template: email content
    :param environment: template params
    :return: email send response
    """
    if environment is None:
        environment = {}

    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"

    # email message
    message = emails.Message(
        subject=T(subject_template),
        html=T(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL)
    )

    # smtp server
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD

    # send
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logger.info(f"send email result: {response}")
