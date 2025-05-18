from base.models import BaseModel
from django.db import models
from django.contrib.auth import get_user_model
from courses.models import Course

UserModel = get_user_model()


class Assignment(BaseModel):
    title = models.TextField(null=True)
    description = models.TextField(null=True)
    cover_image = models.TextField(null=True)
    duration = models.IntegerField(null=True)
    deadline = models.DateTimeField(null=True)
    allowed_attempts = models.IntegerField(null=True)
    created_by = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="created_assignment",
        null=True,
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title


class AssignmentQuestion(BaseModel):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        null=True,
        related_name="assignment_question",
    )
    text = models.TextField(null=True)


class AssignmentQuestionOption(BaseModel):
    question = models.ForeignKey(
        AssignmentQuestion, on_delete=models.CASCADE, related_name="assignment_options"
    )
    text = models.CharField(max_length=255, null=True)
    is_correct = models.BooleanField(default=False)


class AssignmentAttempt(BaseModel):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    is_passed = models.BooleanField(default=False)


class UserQuestionResponse(BaseModel):
    attempt = models.ForeignKey(
        AssignmentAttempt, on_delete=models.CASCADE, related_name="responses"
    )
    question = models.ForeignKey(AssignmentQuestion, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(
        AssignmentQuestionOption, on_delete=models.CASCADE
    )
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ("attempt", "question")


# Create your models here.
