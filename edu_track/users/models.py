from django.contrib.auth.hashers import (
    check_password,
    make_password,
)
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser
from base.models import BaseModel


class User(BaseModel, AbstractBaseUser):
    email = models.EmailField(_("email address"), unique=True, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    password = models.CharField(_("password"), max_length=128, blank=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def clean(self):
        super().clean()
        self.email = self.email.lower()

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """

        def setter(raw_password):
            self.set_password(raw_password)
            self.save(update_fields=["password"])

        return check_password(raw_password, self.password, setter)

    def name(self):
        return f"{self.first_name} {self.last_name}"

    def get_role(self):
        user_role = self.roles.first()
        return user_role.role if user_role else None


class EmailValidationTokens(models.Model):
    email = models.EmailField()
    token = models.TextField("reset_token")
    isValid = models.BooleanField(null=True, default=False)

    expiresAt = models.DateTimeField("expires_at")
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


"""
i can add more profile model based on requirement for students and teachers
eg Student model and Instructor model that can be called upon user creation
"""
