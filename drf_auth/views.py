from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_auth.app_settings import DRF_AUTH_SETTINGS
from drf_auth.serializers import (
    CustomTokenObtainPairSerializer,
    JWTSerializer,
    OTPSerializer,
    UserSerializer,
)
from drf_auth.utils import generate_otp, send_otp, validate_otp
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class RegisterView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        if not DRF_AUTH_SETTINGS.get("EMAIL_OPTIONAL", True):
            if serializer.validated_data.get("email", None) is None:
                raise ValidationError({"email": [_("Email is required.")]})
        if not DRF_AUTH_SETTINGS.get("MOBILE_OPTIONAL", False):
            if serializer.validated_data.get("mobile", None) is None:
                raise ValidationError({"mobile": [_("Mobile is required.")]})
        if "email" in serializer.validated_data.keys():
            if (
                User.objects.filter(email=serializer.validated_data["email"])
                .exclude(username=serializer.validated_data["username"])
                .count()
                > 0
            ):
                raise ValidationError(
                    {"email": [_("A user with that email already exists.")]}
                )
        data = {
            "username": serializer.validated_data["username"],
            "name": serializer.validated_data["name"],
            "password": serializer.validated_data["password"],
            "email": serializer.validated_data.get("email", None),
            "mobile": serializer.validated_data.get("mobile", None),
            "is_active": True,
        }
        return User.objects.create_user(**data)


class LoginView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {
            "user": serializer.user,
            "access_token": serializer.validated_data.get("access"),
            "refresh_token": serializer.validated_data.get("refresh"),
        }
        user = serializer.user
        user.last_login = timezone.now()
        user.save()
        jwtserializer = JWTSerializer(
            instance=data, context=self.get_serializer_context()
        )
        return Response(jwtserializer.data, status=status.HTTP_200_OK)


class OTPView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = OTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        destination = serializer.validated_data.get("destination")
        prop = serializer.validated_data.get("prop")
        is_login = serializer.validated_data.get("is_login")

        if "otp" in request.data.keys():
            if validate_otp(destination, request.data.get("otp")):
                if is_login:
                    user = serializer.user
                    user.last_login = timezone.now()
                    user.save()
                    token = RefreshToken.for_user(user)
                    if hasattr(user, "email"):
                        token["email"] = user.email
                    if hasattr(user, "mobile"):
                        token["mobile"] = user.mobile
                    if hasattr(user, "name"):
                        token["name"] = user.name
                    data = {
                        "user": user,
                        "access_token": str(token.access_token),
                        "refresh_token": str(token),
                    }
                    jwtserializer = JWTSerializer(instance=data)
                    return Response(jwtserializer.data, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response(
                        data={
                            "OTP": [
                                _("OTP Validated successfully!"),
                            ]
                        },
                        status=status.HTTP_202_ACCEPTED,
                    )
        else:
            otp_obj = generate_otp(prop, destination)
            sentotp = send_otp(destination, otp_obj)

            if sentotp["success"]:
                otp_obj.send_counter += 1
                otp_obj.save()

                return Response(sentotp, status=status.HTTP_201_CREATED)
            else:
                raise APIException(
                    detail=_("A Server Error occurred: " + sentotp["message"])
                )


class RetrieveUpdateUserAccountView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        if "email" in request.data.keys():
            if (
                User.objects.filter(email=request.data["email"])
                .exclude(id=self.request.user.id)
                .count()
                > 0
            ):
                raise ValidationError(
                    {"email": ["A user with that email already exists."]}
                )

        resp = super(RetrieveUpdateUserAccountView, self).update(
            request, *args, **kwargs
        )
        if "password" in request.data.keys():
            request.user.set_password(request.data["password"])
            request.user.save()
        return resp
