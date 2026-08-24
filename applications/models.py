import os
import uuid

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils import timezone

private_resume_storage = FileSystemStorage(
    location=os.path.join(settings.BASE_DIR, 'resumes')
)
private_cover_letter_storage = FileSystemStorage(
    location=os.path.join(settings.BASE_DIR, 'cover_letters')
)

class Company(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=255, unique=True)
    website = models.URLField(max_length=500, blank=True, default="")
    location = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"


class Application(models.Model):
    class Status(models.TextChoices):
        APPLIED = "APPLIED", "Applied"
        INTERVIEWING = "INTERVIEWING", "Interviewing"
        OFFER = "OFFER", "Offer"
        REJECTED = "REJECTED", "Rejected"

    class Platform(models.TextChoices):
        LINKEDIN = "LINKEDIN", "LinkedIn"
        INDEED = "INDEED", "Indeed"
        COMPANY_SITE = "COMPANY_SITE", "Company Website"
        OTHER = "OTHER", "Other"

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    company = models.ForeignKey(
        "Company",
        on_delete=models.CASCADE,
        related_name="applications",
    )
    job_title = models.CharField(max_length=255)
    job_url = models.URLField(max_length=500, blank=True, null=True)
    job_description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.APPLIED,
    )

    platform = models.CharField(
        max_length=50,
        choices=Platform.choices,
        default=Platform.LINKEDIN,
    )
    resume_file = models.FileField(storage=private_resume_storage, blank=True, null=True)
    cover_letter_file = models.FileField(
        storage=private_cover_letter_storage, blank=True, null=True
    )
    applied_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Application"
        verbose_name_plural = "Applications"

    def __str__(self):
        return f"{self.user} applied for {self.job_title} at {self.company.name}"


    def save(self, *args, **kwargs):
        if not self.applied_date:
            self.applied_date = timezone.localdate()
        super().save(*args, **kwargs)
