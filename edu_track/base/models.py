import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class BaseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def get_deleted_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=False)

    def get_all_queryset(self):
        return super().get_queryset()


class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True, null=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(_("deleted"), null=True, blank=True)

    objects = BaseManager()

    class Meta:
        abstract = True

    def soft_delete(self):
        """soft delete objects"""
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save(update_fields=["deleted_at", "is_deleted", "updated_at"])

    def restore(self):
        """restore soft-deleted object"""
        self.deleted_at = None
        self.is_deleted = False
        self.save(update_fields=["deleted_at", "is_deleted", "updated_at"])
