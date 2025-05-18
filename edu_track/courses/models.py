from django.db import models
from django.utils.translation import gettext_lazy as _
from base.models import BaseModel
from users.models import User


class Status(models.TextChoices):
    DRAFT = ("draft", _("Draft"))
    PUBLISHED = ("published", _("Published"))


class CourseContentTypes(models.TextChoices):
    DOCUMENT = ("document", _("Document"))
    VIDEO = ("video", _("Video"))


class CourseStudentStatus(models.TextChoices):
    PENDING = ("pending", _("Pending"))
    ACTIVE = ("active", ("Active"))
    SUSPENDED = ("suspended", _("Suspended"))


class Course(BaseModel):
    title = models.CharField(_("title"), max_length=150, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    publish_status = models.CharField(choices=Status.choices, default=Status.PUBLISHED)
    content_url = models.URLField(null=True)
    content_type = models.CharField(
        choices=CourseContentTypes.choices, null=False, blank=False
    )
    metadata = models.JSONField(null=True)

    cover_image = models.URLField(null=True, blank=True)
    is_open_for_enrollment = models.BooleanField(default=True)
    duration = models.CharField(_("duration"), max_length=150, null=True, blank=True)
    created_by = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="created_courses"
    )

    class Meta:
        ordering = ["-created_at"]

    def enrol_user(self, user: "User"):
        return CourseStudent.objects.get_or_create(course=self, user=user)


class CourseStudent(BaseModel):
    course = models.ForeignKey(
        Course, on_delete=models.SET_NULL, null=True, related_name="students"
    )
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="courses"
    )
    status = models.CharField(
        choices=CourseStudentStatus.choices,
        default=CourseStudentStatus.ACTIVE,
    )

    class Meta:
        unique_together = ("user", "course")
