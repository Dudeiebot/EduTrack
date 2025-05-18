import logging
from django.db import transaction
from .serializers import (
    UserSerializer,
    CustomJSONWebTokenSerializer,
)
from django.utils.translation import gettext_lazy as _
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated, AllowAny
from edu_track.backends import CustomJWTAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from .utils import (
    setupEmailValidationToken,
    getUserByEmail,
    getEmailValidationToken,
    sendTokenEmail,
    validateEmailToken,
)


logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomJSONWebTokenSerializer

    def post(self, request, *args, **kwargs) -> Response:
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    pass


@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
class UserLogoutView(APIView):

    def post(self, request):
        try:
            access_token = request.auth
            return Response(
                {"detail": _("Successfully logged out.")}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": _("Invalid token or token not provided.")},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SendTokenView(APIView):
    def post(self, request, format=None):
        email = request.data["email"]
        user = getUserByEmail(email)
        if not user:
            return Response(
                {"message": _("User with that email does not exist")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.email_verified:
            logger.info(f"User has already verified their email: {email}")
            return Response(
                {"message": _("User already verified")},
                status=status.HTTP_400_BAD_REQUEST,
            )
            emailTokenRecord = getEmailValidationToken(email)
            if not emailTokenRecord:
                emailTokenRecord = setupEmailValidationToken(email)
                sendTokenEmail(emailTokenRecord.token, email, user.first_name)
        return Response({"message": _("success")})

    @staticmethod
    def post_extra_actions():
        return []

    def get_authenticators(self):
        if self.request.method == "POST":
            return []
        return super().get_authenticators()

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return super().get_permissions()


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                user = serializer.save()

                refresh = RefreshToken.for_user(user)
                access = refresh.access_token

                response_data = {
                    "user": serializer.data,
                    "email_verified": user.email_verified,
                    "accessToken": str(access),
                    "refreshToken": str(refresh),
                    "message": _("Registration successful"),
                }

                return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            return Response(
                {
                    "error": _("Registration failed. Please try again."),
                    "message error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def patch(self, request):
        user = request.user
        data = request.data.copy()

        if "password" in data:
            return Response(
                {"error": _("Password cannot be updated via this endpoint.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = UserSerializer(user, data=data, partial=True)

        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            serializer.save()
            return Response(
                {
                    "message": _("User details updated successfully"),
                    "user": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error updating user details: {str(e)}")
            return Response(
                {"error": _("Update failed. Please try again.")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ValidateTokenView(APIView):

    def post(self, request, format=None):
        validateFor = request.query_params.get("for")
        token = request.data["token"]
        logger.info(f"Request Data: {request.data}")
        if validateFor == "verify":
            emailTokenRecord = validateEmailToken(token)
            isValid = True if emailTokenRecord else False
            if not isValid:
                return Response(
                    {"message": _("Invalid Token")}, status=status.HTTP_400_BAD_REQUEST
                )
        return Response({"message": _("Token is Valid")})

    @staticmethod
    def post_extra_actions():
        return []

    def get_authenticators(self):
        if self.request.method == "POST":
            return []
        return super().get_authenticators()

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return super().get_permissions()


# Create your views here.
