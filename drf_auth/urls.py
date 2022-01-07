from django.urls import path
from drf_auth import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

app_name = "drf_auth"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="Login"),
    path("register/", views.RegisterView.as_view(), name="Register"),
    path("otp/", views.OTPView.as_view(), name="OTP"),
    path(
        "me/",
        views.RetrieveUpdateUserAccountView.as_view(),
        name="Retrieve Update Profile",
    ),
]

urlpatterns += [
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
