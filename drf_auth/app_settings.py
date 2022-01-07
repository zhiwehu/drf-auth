from django.conf import settings

DEFAULT_DRF_AUTH_SETTINGS = {
    "MOBILE_OPTIONAL": True,
    "EMAIL_OPTIONAL": True,
    "DEFAULT_ACTIVE_STATE": False,
    "OTP": {
        "LENGTH": 6,
        "ALLOWED_CHARS": "1234567890",
        "VALIDATION_ATTEMPTS": 3,
        "SUBJECT": "OTP for Verification",
        "COOLING_PERIOD": 3,
    },
    "MOBILE_VALIDATION": True,
    "EMAIL_VALIDATION": False,
    "REGISTRATION": {
        "SEND_MAIL": False,
        "SEND_MESSAGE": False,
        "MAIL_SUBJECT": "Welcome to DRF-USER",
        "SMS_BODY": "Your account has been created",
        "TEXT_MAIL_BODY": "Your account has been created.",
        "HTML_MAIL_BODY": "Your account has been created.",
    },
}

DRF_AUTH_SETTINGS = getattr(settings, "DRF_AUTH_SETTINGS", DEFAULT_DRF_AUTH_SETTINGS)
