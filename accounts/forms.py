from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .permissions import role_for

class CampusAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if role_for(user) is None:
            raise ValidationError("This account needs a valid campus role. Contact your project team.", code="invalid_role")
