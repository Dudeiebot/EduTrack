from .models import User, EmailValidationTokens
from django.utils import timezone
from datetime import timedelta
import random, logging
from django.core.exceptions import ObjectDoesNotExist
from base.utils import sendEmail
from roles.models import Role, RoleTypes, UserRole
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError

logger = logging.getLogger(__name__)


def sendTokenEmail(token, email, first_name):
    try:
        content = f"""\
        <!DOCTYPE html>
        <html>
        <head>
            <title>Welcome to EduTrack</title>
        </head>
        <body>
            <p>Hello {first_name},</p>
            <p> Please verify your email address to begin.</p>
            <p><strong>Token:</strong> {token} (expires in 5 minutes)</p>
            <p>Once verified, here’s how to get started:</p>
            <p>Your learning journey starts here!</p>
            <p>Welcome aboard,<br><strong>The EduTrack Team</strong></p>
        </body>
        </html>
        """

        sendEmail(email, content, "Verify Your Email")
    except Exception as e:
        return None


def get_roles():
    roles = {}
    try:
        roles["student"] = Role.objects.get(name=RoleTypes.TRAINEE)
        roles["instructor"] = Role.objects.get(name=RoleTypes.INSTRUCTOR)
    except ObjectDoesNotExist as e:
        logger.error(e)
    return roles


"""
dependant if a user can have multiple account or not
"""


def user_roles(user, role):
    try:
        existing_role = UserRole.objects.filter(user=user).first()

        if existing_role:
            raise ValidationError("User already has a role")
        return UserRole.objects.create(user=user, role=role)

    except IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
        raise ValidationError("Database constraint violation")
    except Exception as e:
        logger.error(f"Unexpected error in user role assignment: {e}")
        raise ValidationError(str(e))


def getExpiresAt(minutes):
    return timezone.now() + timedelta(minutes=minutes)


def getUserByEmail(email):
    try:
        return User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return None


def generateRandomPin(length=6):
    randomlist = random.sample(range(0, 10), length)
    pin = "".join(list(map(str, randomlist)))
    return pin


def setupEmailValidationToken(email):
    try:
        emailValidationTokenRecord = getEmailValidationToken(email)

        if not emailValidationTokenRecord:
            emailValidationTokenRecord = EmailValidationTokens(
                email=email, token=generateRandomPin(), expiresAt=getExpiresAt(5)
            )
            emailValidationTokenRecord.save()

        return emailValidationTokenRecord

    except Exception as e:
        return None


def validateEmailToken(token):
    try:
        emailTokenRecord = EmailValidationTokens.objects.get(token=token)

        if emailTokenRecord.expiresAt >= timezone.now():
            emailTokenRecord.isValid = True
            emailTokenRecord.save()
            return emailTokenRecord

        return None
    except ObjectDoesNotExist:
        return None


def getEmailValidationToken(email):
    try:
        emailValidationTokenRecord = EmailValidationTokens.objects.get(email=email)

        if emailValidationTokenRecord.expiresAt >= timezone.now():
            return emailValidationTokenRecord

        emailValidationTokenRecord.delete()
        return None

    except ObjectDoesNotExist:
        return None
