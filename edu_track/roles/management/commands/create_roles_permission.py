import json
from django.core.management.base import BaseCommand
from roles_and_permissions.models import Operation, Permission, Role, SystemResource


class Command(BaseCommand):
    help = "Create default roles and permissions"

    def handle(self, *args, **kwargs):
        """
        Create default roles and permissions
        """
        f = open("roles/resource.json")
        data = json.load(f)

        operations = {}
        for operation_data in data["operations"]:
            operation, created = Operation.objects.get_or_create(
                type=operation_data["type"],
                defaults={"description": operation_data["description"]},
            )
            operations[operation.type] = operation
            self.stdout.write(
                f"Operation {operation.type} {'created' if created else 'already exists'}."
            )

        resources = {}
        for resource_data in data["resources"]:
            resource, created = SystemResource.objects.get_or_create(
                key=resource_data["key"], defaults={"title": resource_data["title"]}
            )
            resources[resource.key] = resource
            self.stdout.write(
                f"Resource {resource.key} {'created' if created else 'already exists'}."
            )

        roles = {}
        for role_data in data["roles"]:
            role, created = Role.objects.get_or_create(
                name=role_data["name"],
                defaults={"description": role_data["description"]},
            )
            roles[role.name] = role
            self.stdout.write(
                f"Role {role.name} {'created' if created else 'already exists'}."
            )

        for permission_data in data["permissions"]:
            operation = operations[permission_data["operation"]]
            resource = resources[permission_data["resource"]]
            permission, created = Permission.objects.get_or_create(
                operation=operation,
                resource=resource,
                defaults={"title": f"{operation.type.lower()}_{resource.key}"},
            )
            for role_name in permission_data["roles"]:
                role = roles[role_name]
                role.permissions.add(permission)
                self.stdout.write(
                    f"Permission {permission.title} assigned to {role.name}."
                )

        self.stdout.write(
            self.style.SUCCESS("Default roles and permissions have been created.")
        )
