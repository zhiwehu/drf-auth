import datetime

import pytz
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_auth.app_settings import DRF_AUTH_SETTINGS
from drf_auth.models import OTPValidation
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    NotFound,
    PermissionDenied,
)

otp_settings = DRF_AUTH_SETTINGS.get("OTP", {})

User = get_user_model()


def check_validation(value):
    try:
        otp_object = OTPValidation.objects.get(destination=value)
        return otp_object.is_validated
    except OTPValidation.DoesNotExist:
        return False


def validate_otp(value, otp):
    try:
        otp_object = OTPValidation.objects.get(destination=value, is_validated=False)

        otp_object.validate_attempt -= 1

        if str(otp_object.otp) == str(otp):
            otp_object.is_validated = True
            otp_object.save()
            return True

        elif otp_object.validate_attempt <= 0:
            generate_otp(otp_object.prop, value)
            raise AuthenticationFailed(
                detail=_("Incorrect OTP. Attempt exceeded! OTP has been " "reset.")
            )

        else:
            otp_object.save()
            raise AuthenticationFailed(
                detail=_(
                    "OTP Validation failed! "
                    + str(otp_object.validate_attempt)
                    + " attempts left!"
                )
            )

    except OTPValidation.DoesNotExist:
        raise NotFound(
            detail=_(
                "No pending OTP validation request found for provided "
                "destination. Kindly send an OTP first"
            )
        )


def generate_otp(prop, value):
    random_number = User.objects.make_random_password(
        length=otp_settings.get("LENGTH", 6),
        allowed_chars=otp_settings.get("ALLOWED_CHARS", "1234567890"),
    )

    while OTPValidation.objects.filter(otp__exact=random_number).filter(
        is_validated=False
    ):
        random_number = User.objects.make_random_password(
            length=otp_settings.get("LENGTH", 6),
            allowed_chars=otp_settings.get("ALLOWED_CHARS", "1234567890"),
        )

    try:
        otp_object = OTPValidation.objects.get(destination=value)
    except OTPValidation.DoesNotExist:
        otp_object = OTPValidation()
        otp_object.destination = value
    else:
        if not datetime_passed_now(otp_object.reactive_at):
            return otp_object

    otp_object.otp = random_number
    otp_object.prop = prop

    otp_object.is_validated = False

    otp_object.validate_attempt = otp_settings["VALIDATION_ATTEMPTS"]

    otp_object.reactive_at = timezone.now() - datetime.timedelta(minutes=1)
    otp_object.save()
    return otp_object


def datetime_passed_now(source):
    if source.tzinfo is not None and source.tzinfo.utcoffset(source) is not None:
        return source <= datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    else:
        return source <= datetime.datetime.now()


def send_otp(value, otpobj):
    otp = otpobj.otp

    if not datetime_passed_now(otpobj.reactive_at):
        raise PermissionDenied(
            detail=_("OTP sending not allowed until: " + str(otpobj.reactive_at))
        )

    message = (
        "OTP for verifying "
        + otpobj.get_prop_display()
        + ": "
        + value
        + " is "
        + otp
        + ". Don't share this with anyone!"
    )

    try:
        rdata = send_message(message, otp_settings["SUBJECT"], value)
    except ValueError as err:
        raise APIException(_("Server configuration error occured: %s") % str(err))

    otpobj.reactive_at = timezone.now() + datetime.timedelta(
        minutes=otp_settings["COOLING_PERIOD"]
    )
    otpobj.save()

    return rdata


def send_message(message: str, subject: str, recip: str, html_message: str = None):
    """
    Sends message to specified value.
    Source: Himanshu Shankar (https://github.com/iamhssingh)
    Parameters
    ----------
    message: str
        Message that is to be sent to user.
    subject: str
        Subject that is to be sent to user, in case prop is an email.
    recip: str
        Recipient to whom message is being sent.
    html_message: str
        HTML variant of message, if any.

    Returns
    -------
    sent: dict
    """

    import smtplib

    from django.conf import settings
    from django.core.mail import send_mail
    from sendsms import api

    sent = {"success": False, "message": None}

    # Check if the value of recipient is valid (min length: a@b.c)
    if len(recip) < 5:
        raise ValueError("Invalid recipient.")

    is_email = True
    try:
        validate_email(recip)
    except Exception as e:
        print(e)
        is_email = False

    if is_email:
        if not getattr(settings, "EMAIL_HOST", None):
            raise ValueError(
                "EMAIL_HOST must be defined in django " "setting for sending mail."
            )
        if not getattr(settings, "EMAIL_FROM", None):
            raise ValueError(
                "EMAIL_FROM must be defined in django setting "
                "for sending mail. Who is sending email?"
            )
        try:
            send_mail(
                subject=subject,
                message=message,
                html_message=html_message,
                from_email=settings.EMAIL_FROM,
                recipient_list=[recip],
            )
        except smtplib.SMTPException as ex:
            sent["message"] = "Message sending failed!" + str(ex.args)
            sent["success"] = False
        else:
            sent["message"] = "Message sent successfully!"
            sent["success"] = True
    else:
        try:
            api.send_sms(body=message, to=[recip], from_phone=None)
        except Exception as ex:
            sent["message"] = "Message sending Failed!" + str(ex.args)
            sent["success"] = False
        else:
            sent["message"] = "Message sent successfully!"
            sent["success"] = True

    return sent
