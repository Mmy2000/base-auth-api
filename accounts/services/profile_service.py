from typing import Dict, Optional
from accounts.models import User


class ProfileUpdateService:
    """
    Service for updating user profile
    Follows Single Responsibility Principle
    """

    def update_profile(
        self, user: User, profile_data: Dict
    ) -> tuple[Optional[object], Optional[str]]:
        """
        Update user and profile information
        Returns: (profile, error_message)
        """
        try:
            # Separate user fields from profile fields
            user_fields = ["first_name", "last_name", "username"]
            profile_fields = [
                "image",
                "country",
                "city",
                "phone_number",
                "address_line_1",
                "address_line_2",
            ]

            # Update user fields
            user_updated = False
            for field in user_fields:
                if field in profile_data:
                    # Validate username uniqueness if being updated
                    if field == "username":
                        new_username = profile_data[field]
                        if (
                            User.objects.filter(username=new_username)
                            .exclude(pk=user.pk)
                            .exists()
                        ):
                            return None, "Username already exists"

                    setattr(user, field, profile_data[field])
                    user_updated = True

            if user_updated:
                user.save()

            # Update profile fields
            profile = user.profile
            profile_updated = False

            for field in profile_fields:
                if field in profile_data:
                    setattr(profile, field, profile_data[field])
                    profile_updated = True

            if profile_updated:
                profile.save()

            # Refresh profile to get updated user data
            profile.refresh_from_db()

            return profile, None

        except Exception as e:
            return None, f"Profile update failed: {str(e)}"
