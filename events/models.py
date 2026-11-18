from django.conf import settings
from django.db import models
from django.db.models import Q, F
from django.core.validators import MinValueValidator, MaxValueValidator, MaxLengthValidator


class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = "Draft"
        PUBLISHED = "Published"
        CANCELLED = "Cancelled"

    title = models.CharField(max_length=120)
    description = models.TextField(validators=[MaxLengthValidator(2000)])
    category = models.CharField(max_length=60)
    venue = models.CharField(max_length=120)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    registration_closes_at = models.DateTimeField()
    capacity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(200)])
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_events")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="cancelled_events")
    cancellation_reason = models.CharField(max_length=500, blank=True)
    allocation_version = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["start_at", "id"]
        indexes = [models.Index(fields=["status", "start_at"])]
        constraints = [
            models.CheckConstraint(condition=Q(capacity__gte=1, capacity__lte=200), name="event_capacity_1_200"),
            models.CheckConstraint(condition=Q(registration_closes_at__lt=F("start_at")) & Q(start_at__lt=F("end_at")), name="event_time_order"),
            models.CheckConstraint(condition=Q(status__in=["Draft", "Published", "Cancelled"]), name="valid_event_status"),
        ]

    def __str__(self):
        return self.title
