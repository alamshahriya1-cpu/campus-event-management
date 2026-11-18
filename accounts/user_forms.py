"""Forms for organizer maintenance of existing student accounts."""
from django import forms
from django.contrib.auth.forms import SetPasswordForm

from .models import StudentProfile


class ListedFieldsOnly:
    def clean(self):
        cleaned = super().clean()
        if set(self.data) - set(self.fields) - {"csrfmiddlewaretoken"}:
            raise forms.ValidationError("Only the fields shown on this form can be changed.")
        return cleaned


class StudentDetailsForm(ListedFieldsOnly, forms.Form):
    first_name = forms.CharField(label="First name", max_length=150)
    last_name = forms.CharField(label="Last name", max_length=150, required=False)
    student_number = forms.CharField(label="Student ID", max_length=20)
    email = forms.EmailField(label="Email address", max_length=254, required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        kwargs.setdefault("initial", {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "student_number": user.student_profile.student_number,
            "email": user.email,
        })
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control", "autocomplete": "off"})

    def clean_student_number(self):
        number = self.cleaned_data["student_number"]
        if StudentProfile.objects.filter(student_number__iexact=number).exclude(user=self.user).exists():
            raise forms.ValidationError("This student ID is already assigned to another account.")
        return number

    def save(self):
        # The view wraps both writes in one transaction. Registration foreign keys
        # use the unchanged user ID, so names/identifiers do not change allocations.
        for field in ("first_name", "last_name", "email"):
            setattr(self.user, field, self.cleaned_data[field])
        self.user.save(update_fields=["first_name", "last_name", "email"])
        profile = self.user.student_profile
        profile.student_number = self.cleaned_data["student_number"]
        profile.save(update_fields=["student_number"])
        return self.user


class StudentPasswordForm(ListedFieldsOnly, SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields["new_password2"].label = "Confirm new password"
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control", "autocomplete": "new-password"})
