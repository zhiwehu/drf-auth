=====
drf-auth
=====

Drf-auth is a Django rest framework auth app.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "drf_auth" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'rest_framework',
        'drf_auth',
    ]

2. Change the settings.py::

    AUTHENTICATION_BACKENDS = [
        'drf_auth.auth.MultiFieldModelBackend',
    ]

    AUTH_USER_MODEL = 'drf_auth.User'

    REST_FRAMEWORK = {
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework_simplejwt.authentication.JWTAuthentication",
        ),
    }

    DRF_AUTH_SETTINGS = {
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
        "EMAIL_VALIDATION": True,
        "REGISTRATION": {
            "SEND_MAIL": True,
            "SEND_MESSAGE": True,
            "MAIL_SUBJECT": "Welcome to DRF-AUTH",
            "SMS_BODY": "Your account has been created",
            "TEXT_MAIL_BODY": "Your account has been created.",
            "HTML_MAIL_BODY": "Your account has been created.",
        },
    }

    SENDSMS_BACKEND = "sendsms.backends.console.SmsBackend"

3. Include the URLconf in your project urls.py like this::

    path('api/auth/', include('drf_auth.urls')),

4. Run ``python manage.py migrate`` to create the polls models.

5. Visit http://127.0.0.1:8000/api/auth/login/
