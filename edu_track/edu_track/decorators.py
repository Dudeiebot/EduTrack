from functools import wraps
from rest_framework.response import Response
from rest_framework import status


def adminRequired(view_method):
    @wraps(view_method)
    def _wrapped_view(self, *args, **kwargs):
        if self.request.user.get_role.name not in ("SYSTEM_ADMIN"):
            return Response(
                {"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )
        return view_method(self, *args, **kwargs)

    return _wrapped_view
