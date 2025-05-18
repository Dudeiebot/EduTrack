from functools import wraps
from rest_framework import status, response


def permission_required(permission):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view, request, *args, **kwargs):
            _user = getattr(request, "user")
            role = _user.get_role()
            operation, resource_key = permission.split("_", 1)
            if role and role.has_permission(operation, resource_key):
                return view_func(view, request, *args, **kwargs)

            return response.Response(
                {"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        return _wrapped_view

    return decorator
