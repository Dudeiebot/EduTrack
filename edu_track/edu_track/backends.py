import logging
from django.contrib.auth.backends import ModelBackend
from django.db.models.query_utils import logging
from users.models import User
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.authentication import JWTAuthentication


logger = logging.getLogger(__name__)


class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email__iexact=email)
            if user and check_password(password, user.password):
                return user
        except User.DoesNotExist:
            return None


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        return self.get_user(validated_token), validated_token

    def get_user(self, validated_token):
        """
        Retrieve the user based on the validated token.
        """
        try:
            user_id = validated_token["user_id"]
            user = User.objects.get(uid=user_id)
            return user
        except User.DoesNotExist:
            return None
