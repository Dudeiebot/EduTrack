from django.contrib.auth import get_user_model
from django.db import models
from base.models import BaseModel


UserModel = get_user_model()


class RoleTypes(models.TextChoices):
    INSTRUCTOR = "Instructor", ("Instructor")
    STUDENT = "Student", ("Student")
    SYSTEM_ADMIN = "SystemAdmin", ("System Admin")


class PlatformActors(models.TextChoices):
    SYSTEM = "SYSTEM", ("SYSTEM")
    USER = "USER", ("USER")


class RoleOperationTypes(models.TextChoices):
    CREATE = "CREATE", ("CREATE")
    VIEW = "VIEW", ("VIEW")
    UPDATE = "UPDATE", ("UPDATE")
    DELETE = "DELETE", ("DELETE")


class Operation(BaseModel):
    type = models.CharField(
        max_length=100,
        choices=RoleOperationTypes.choices,
        null=True,
        blank=False,
    )
    description = models.TextField(null=True)


class SystemResource(BaseModel):
    key = models.TextField(unique=True, null=True)
    title = models.CharField(max_length=100, null=True)


class Permission(BaseModel):
    operation = models.ForeignKey(Operation, on_delete=models.SET_NULL, null=True)
    resource = models.ForeignKey(SystemResource, on_delete=models.SET_NULL, null=True)
    title = models.TextField(null=True)
    description = models.TextField(null=True)
    created_by = models.ForeignKey(
        UserModel,
        related_name="created_permissions",
        on_delete=models.SET_NULL,
        null=True,
    )
    created_by_category = models.CharField(
        max_length=100,
        choices=PlatformActors.choices,
        default=PlatformActors.SYSTEM,
        null=True,
        blank=False,
    )


class Role(BaseModel):
    name = models.CharField(choices=RoleTypes.choices, max_length=100, null=True)
    description = models.TextField(null=True)
    disabled = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        UserModel, related_name="created_roles", on_delete=models.SET_NULL, null=True
    )
    created_by_category = models.CharField(
        max_length=100,
        choices=PlatformActors.choices,
        default=PlatformActors.SYSTEM,
        null=True,
        blank=False,
    )
    permissions = models.ManyToManyField(Permission)

    def has_permission(self, operation, resource_key):
        return self.permissions.filter(
            operation__type=operation.upper(), resource__key=resource_key
        ).exists()


class UserRole(BaseModel):
    user = models.ForeignKey(
        UserModel, related_name="roles", on_delete=models.SET_NULL, null=True
    )
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ["user", "role"]


# Create your models here.
