from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DRFAuthConfig(AppConfig):
    name = "drf_auth"
    verbose_name = _("DRF Auth")
