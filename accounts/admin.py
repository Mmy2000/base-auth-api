"""
Django Admin Configuration
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile


class ProfileInline(admin.StackedInline):
    """Inline Profile in User Admin"""

    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


class UserAdmin(BaseUserAdmin):
    """Custom User Admin"""

    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "date_joined",
    )
    list_filter = ("is_active", "is_staff", "is_admin", "is_superadmin", "date_joined")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("username", "first_name", "last_name")}),
        ("OTP", {"fields": ("otp", "otp_expiry")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_admin", "is_superadmin")},
        ),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    readonly_fields = ("date_joined", "last_login")
    filter_horizontal = ()
    inlines = (ProfileInline,)


class ProfileAdmin(admin.ModelAdmin):
    """Profile Admin"""

    list_display = ("user", "country", "city", "phone_number", "created_at")
    list_filter = ("country", "city", "created_at")
    search_fields = ("user__email", "user__username", "country", "city", "phone_number")
    ordering = ("-created_at",)

    fieldsets = (
        ("User", {"fields": ("user",)}),
        ("Profile Image", {"fields": ("image",)}),
        ("Location", {"fields": ("country", "city")}),
        ("Contact", {"fields": ("phone_number",)}),
        ("Address", {"fields": ("address_line_1", "address_line_2")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    readonly_fields = ("created_at", "updated_at")


# Register models
admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
