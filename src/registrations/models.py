from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Registration(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "Confirmed"
        WAITLISTED = "Waitlisted"
        CANCELLED = "Cancelled"

    event = models.ForeignKey("events.Event", on_delete=models.PROTECT, related_name="registrations")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="registrations")
    status = models.CharField(max_length=12, choices=Status.choices)
    joined_at = models.DateTimeField(default=timezone.now)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_source = models.CharField(max_length=7, choices=[("Student", "Student"), ("Event", "Event")], null=True, blank=True)
    attended = models.BooleanField(default=False)
    attendance_updated_at = models.DateTimeField(null=True, blank=True)
    attendance_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="attendance_updates")

    class Meta:
        ordering = ["joined_at", "id"]
        constraints = [
            models.UniqueConstraint(fields=["event", "student"], name="one_registration_per_student_event"),
            models.CheckConstraint(condition=Q(status__in=["Confirmed", "Waitlisted", "Cancelled"]), name="valid_registration_status"),
            models.CheckConstraint(condition=Q(attended=False) | Q(status="Confirmed"), name="attendance_requires_confirmed"),
        ]
        indexes = [models.Index(fields=["event", "status", "joined_at"])]
