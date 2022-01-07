import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


def auto_unique_upload_image(instance, filename):
    try:
        ext = filename.split(".")[-1]
    except Exception as e:
        ext = ""
    if ext:
        filename = "%s.%s" % (str(uuid.uuid4()), ext)
    else:
        filename = str(uuid.uuid4())
    return "/".join(["model", "image", instance._meta.model_name, filename])


class User(AbstractUser):
    email = models.EmailField(
        _("email address"), blank=True, null=True, unique=True, db_index=True
    )
    mobile = models.CharField(
        verbose_name=_("Mobile Number"),
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
    )
    name = models.CharField(verbose_name=_("Full Name"), max_length=500, blank=False)
    image = models.ImageField(
        verbose_name=_("Profile Photo"), upload_to=auto_unique_upload_image, blank=True
    )

    def get_full_name(self):
        return str(self.name)

    def __str__(self):
        return str(self.name) + " | " + str(self.username)


class OTPValidation(TimeStampedModel):
    EMAIL = "E"
    MOBILE = "M"
    PROP_CHOICES = ((EMAIL, _("Email")), (MOBILE, _("Mobile")))

    otp = models.CharField(verbose_name=_("OTP Code"), max_length=10)
    destination = models.CharField(
        verbose_name=_("Destination Address (Mobile/Email)"),
        max_length=150,
        unique=True,
    )
    is_validated = models.BooleanField(verbose_name=_("Is Validated"), default=False)
    validate_attempt = models.IntegerField(
        verbose_name=_("Attempted Validation"), default=3
    )
    prop = models.CharField(
        verbose_name=_("Destination Property"),
        default=EMAIL,
        max_length=1,
        choices=PROP_CHOICES,
    )
    send_counter = models.PositiveIntegerField(
        verbose_name=_("OTP Sent Counter"), default=0
    )
    reactive_at = models.DateTimeField(verbose_name=_("ReActivate Sending OTP"))

    def __str__(self):
        return self.destination

    class Meta:
        verbose_name = _("OTP Validation")
        verbose_name_plural = _("OTP Validations")
