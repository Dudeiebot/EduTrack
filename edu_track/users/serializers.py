from rest_framework import serializers
from .models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .utils import get_roles, user_roles
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate, get_user_model

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    email = serializers.EmailField(required=True)
    account_type = serializers.CharField(write_only=True, required=True)
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "uid",
            "first_name",
            "last_name",
            "email",
            "email_verified",
            "password",
            "role",
        )
        required_fields = [
            "first_name",
            "last_name",
            "password",
        ]
        read_only_fields = [
            "uid",
        ]

    def validate_email(self, email: str):
        if isinstance(email, str):
            email = email.lower()
        return email

    def create(self, validated_data):
        account_type = validated_data.pop("account_type", None)
        password = validated_data.pop("password", None)

        roles = get_roles()
        _user = self.Meta.model.objects.create(**validated_data)

        if account_type == "student":
            role = roles.get("student")
        else:
            role = roles.get("instructor")

        user_roles(_user, role)

        if password:
            _user.set_password(password)
            _user.save(update_fields=["password"])

        return _user

    def get_role(self, instance: User):
        role_object = instance.roles.first()
        if not role_object:
            return None
        return role_object.role.name


class CustomJSONWebTokenSerializer(TokenObtainPairSerializer):
    username_field = "email"

    def validate(self, attrs):
        data = super().validate(attrs)

        email = attrs.get("email")
        password = attrs.get("password")

        if not (email and password):
            raise serializers.ValidationError(_("Must include 'email' and 'password'."))

        user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )

        if not user:
            raise serializers.ValidationError(
                _("Unable to log in with provided credentials.")
            )

        if hasattr(user, "disabled") and user.disabled:
            raise serializers.ValidationError(
                _("Account is disabled. Please contact support for assistance.")
            )
        refresh = self.get_token(user)
        serialized_data = UserSerializer(user).data

        serialized_data.update(
            {
                "account_type": user.account_type,
                "refreshToken": str(refresh),
                "accessToken": str(refresh.access_token),
                "last_login": timezone.now(),
            }
        )

        data.pop("refresh", None)
        data.pop("access", None)

        serialized_data.update(data)
        return serialized_data
