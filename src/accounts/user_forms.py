"""Organizer student creation, ID-based login, and account maintenance."""
from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import Group
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import StudentProfile
from .student_ids import validate_student_id


class ListedFieldsOnly:
    def clean(self):
        cleaned = super().clean()
        if set(self.data) - set(self.fields) - {"csrfmiddlewaretoken"}:
            raise forms.ValidationError("Only the fields shown on this form can be changed.")
        return cleaned


class StudentIdentityForm(ListedFieldsOnly, forms.Form):
    first_name = forms.CharField(label="First name", max_length=150)
    last_name = forms.CharField(label="Last name", max_length=150, required=False)
    student_number = forms.CharField(
        label="Student ID", max_length=20,
        help_text="This is the student's sign-in username. Keep any hyphens and leading zeros.",
    )
    email = forms.EmailField(label="Email address", max_length=254, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control", "autocomplete": "off"})
        self.fields["student_number"].widget.attrs.update({"autocapitalize": "none", "spellcheck": "false"})

    def clean_student_number(self):
        return validate_student_id(self.cleaned_data["student_number"], user=getattr(self, "user", None))


class StudentDetailsForm(StudentIdentityForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        kwargs.setdefault("initial", {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "student_number": user.student_profile.student_number,
            "email": user.email,
        })
        super().__init__(*args, **kwargs)

    @transaction.atomic
    def save(self):
        # The view wraps both writes in one transaction. Registration foreign keys
        # use the unchanged user ID, so names/identifiers do not change allocations.
        for field in ("first_name", "last_name", "email"):
            setattr(self.user, field, self.cleaned_data[field])
        self.user.username = self.cleaned_data["student_number"]
        self.user.save(update_fields=["first_name", "last_name", "email", "username"])
        profile = self.user.student_profile
        profile.student_number = self.cleaned_data["student_number"]
        profile.save(update_fields=["student_number"])
        return self.user


class StudentCreateForm(StudentIdentityForm):
    password1 = forms.CharField(
        label="Initial password", strip=False, widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(label="Confirm password", strip=False, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("password1", "password2"):
            self.fields[name].widget.attrs["autocomplete"] = "new-password"

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password1")
        if password and cleaned.get("password2") and password != cleaned["password2"]:
            self.add_error("password2", "The two passwords do not match.")
        if password:
            candidate = get_user_model()(
                username=cleaned.get("student_number", ""), first_name=cleaned.get("first_name", ""),
                last_name=cleaned.get("last_name", ""), email=cleaned.get("email", ""),
            )
            try:
                password_validation.validate_password(password, candidate)
            except ValidationError as exc:
                self.add_error("password1", exc)
        return cleaned

    @transaction.atomic
    def save(self):
        user = get_user_model().objects.create_user(
            username=self.cleaned_data["student_number"], password=self.cleaned_data["password1"],
            first_name=self.cleaned_data["first_name"], last_name=self.cleaned_data["last_name"],
            email=self.cleaned_data["email"], is_staff=False, is_superuser=False, is_active=True,
        )
        user.groups.set([Group.objects.get_or_create(name="Student")[0]])
        StudentProfile.objects.create(user=user, student_number=self.cleaned_data["student_number"])
        return user


class StudentPasswordForm(ListedFieldsOnly, SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields["new_password2"].label = "Confirm new password"
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control", "autocomplete": "new-password"})


class StudentAccessForm(ListedFieldsOnly, forms.Form):
    confirm = forms.BooleanField(label="I confirm this account access change.")


class StudentDeleteForm(ListedFieldsOnly, forms.Form):
    confirmation_id = forms.CharField(
        label="Type the Student ID to confirm deletion", max_length=20, strip=False,
        widget=forms.TextInput(attrs={
            "class": "form-control", "autocomplete": "off",
            "autocapitalize": "none", "spellcheck": "false",
        }),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_confirmation_id(self):
        value = self.cleaned_data["confirmation_id"]
        if value != self.user.student_profile.student_number:
            raise forms.ValidationError("Enter the exact Student ID shown above.")
        return value
