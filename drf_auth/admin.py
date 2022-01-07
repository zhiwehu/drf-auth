from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.text import gettext_lazy as _
from drf_auth.models import OTPValidation, User


class DRFUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("name", "image", "email", "mobile")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "role",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _("Important dates"),
            {
                "fields": (
                    "date_joined",
                    "last_login",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "mobile", "password1", "password2"),
            },
        ),
    )
    list_display = ("username", "email", "name", "mobile", "is_active")
    search_fields = ("username", "name", "email", "mobile")
    readonly_fields = ("date_joined",)


class OTPValidationAdmin(admin.ModelAdmin):
    list_display = ("destination", "otp", "prop")


admin.site.register(User, DRFUserAdmin)
admin.site.register(OTPValidation, OTPValidationAdmin)
