from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator, ValidationError
from django.utils.translation import gettext_lazy as _
from drf_auth.models import OTPValidation
from drf_auth.utils import check_validation
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(ModelSerializer):

    def validate_email(self, email):
        if check_validation(value=email):
            return email
        else:
            raise ValidationError(_("The email must be pre-validated via OTP."))

    def validate_mobile(self, mobile):
        if check_validation(value=mobile):
            return mobile
        else:
            raise ValidationError(_("The mobile number must be pre-validated via OTP."))

    def validate_password(self, password):
        validate_password(password)
        return password

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "name",
            "email",
            "mobile",
            "image",
            "password"
        )
        extra_kwargs = {"password": {"write_only": True}}


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": _("username or password is invalid.")
    }

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        if hasattr(user, "email"):
            token["email"] = user.email

        if hasattr(user, "mobile"):
            token["mobile"] = user.mobile

        if hasattr(user, "name"):
            token["name"] = user.name

        return token


class JWTSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user_data = UserSerializer(obj["user"], context=self.context).data
        return user_data


class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    is_login = serializers.BooleanField(default=False)
    verify_otp = serializers.CharField(required=False)
    destination = serializers.CharField(required=True)

    def get_user(self, prop, destination):
        if prop == OTPValidation.MOBILE:
            try:
                user = User.objects.get(mobile=destination)
            except User.DoesNotExist:
                user = None
        else:
            try:
                user = User.objects.get(email=destination)
            except User.DoesNotExist:
                user = None

        return user

    def validate(self, attrs: dict) -> dict:
        validator = EmailValidator()
        try:
            validator(attrs["destination"])
            attrs["prop"] = OTPValidation.EMAIL
        except ValidationError:
            attrs["prop"] = OTPValidation.MOBILE

        user = self.get_user(attrs.get("prop"), attrs.get("destination"))

        if not user:
            if attrs["is_login"]:
                raise NotFound(_("No user exists with provided details"))
        else:
            attrs["user"] = user

        return attrs
