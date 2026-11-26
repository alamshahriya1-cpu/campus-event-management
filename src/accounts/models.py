from django.conf import settings
from django.db import models


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, primary_key=True, related_name="student_profile")
    student_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.student_number
