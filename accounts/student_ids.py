"""Student IDs used as login names; preserve hyphens and leading zeros."""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .models import StudentProfile


id_format = RegexValidator(
    r"\A[A-Za-z0-9][A-Za-z0-9_-]{0,19}\Z",
    "Use 1–20 letters or numbers, with hyphens or underscores if needed. Start with a letter or number.",
)


def validate_student_id(number, *, user=None):
    id_format(number)
    profiles = StudentProfile.objects.filter(student_number__iexact=number)
    usernames = get_user_model().objects.filter(username__iexact=number)
    if user is not None:
        profiles = profiles.exclude(user=user)
        usernames = usernames.exclude(pk=user.pk)
    if profiles.exists():
        raise ValidationError("This student ID is already assigned to another account.")
    if usernames.exists():
        raise ValidationError("This student ID is already used as an account login. Choose a different ID.")
    return number
