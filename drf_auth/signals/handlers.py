"""Config for django signals"""
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from drf_auth.app_settings import DRF_AUTH_SETTINGS
from drf_auth.utils import send_message


@receiver(post_save, sender=get_user_model())
def post_register(sender, instance: get_user_model(), created, **kwargs):
    """Sends mail/message to users after registeration

    Parameters
    ----------
    sender: get_user_model()

    instance: get_user_model()

    created: bool
    """

    if created:
        if DRF_AUTH_SETTINGS["REGISTRATION"]["SEND_MAIL"] and instance.email:
            send_message(
                message=DRF_AUTH_SETTINGS["REGISTRATION"]["TEXT_MAIL_BODY"],
                subject=DRF_AUTH_SETTINGS["REGISTRATION"]["MAIL_SUBJECT"],
                recip=instance.email,
                html_message=DRF_AUTH_SETTINGS["REGISTRATION"]["HTML_MAIL_BODY"],
            )
        if DRF_AUTH_SETTINGS["REGISTRATION"]["SEND_MESSAGE"] and instance.mobile:
            send_message(
                message=DRF_AUTH_SETTINGS["REGISTRATION"]["SMS_BODY"],
                subject=DRF_AUTH_SETTINGS["REGISTRATION"]["MAIL_SUBJECT"],
                recip=instance.mobile,
            )
