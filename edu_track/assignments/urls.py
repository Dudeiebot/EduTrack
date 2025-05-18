from django.urls import path
from assignment.views import (
    SubmitAssignmentView,
    AssignmentSubmissionReviewView,
    MarkReviewedView,
    AssignmentWithQuestionsCreateView,
)


urlpatterns = [
    path(
        "/create", AssignmentWithQuestionsCreateView.as_view(), name="create-assignment"
    ),
    path(
        "/<uuid:assignment_uid>/submit",
        SubmitAssignmentView.as_view(),
        name="submit-assignment",
    ),
    path(
        "/<uuid:assignment_uid>/submissions",
        AssignmentSubmissionReviewView.as_view(),
        name="review-submissions",
    ),
    path(
        "<uuid:attempt_uid>/review",
        MarkReviewedView.as_view(),
        name="mark-reviewed",
    ),
]
