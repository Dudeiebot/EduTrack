from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from .models import (
    Assignment,
    AssignmentAttempt,
    CourseAssignment,
    CourseEnrollment,
    AssignmentQuestion,
)
from .serializers import (
    AssignmentSerializer,
    AssignmentWithQuestionsSerializer,
    AssignmentAttemptSerializer,
    AssignmentSubmissionSerializer,
    AssignmentQuestionSerializer,
)
from rest_framework import status
from base.permissions import permission_required
from django.http import Http404


class AssignmentWithQuestionsCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @permission_required("create_assignment")
    def post(self, request):
        serializer = AssignmentWithQuestionsSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        assignment = serializer.save()
        return Response(AssignmentSerializer(assignment).data, status=201)


class AssignmentQuestionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        assignment = Assignment.objects.get(pk=pk)
        serializer = AssignmentSerializer(assignment)
        response_data = serializer.data
        [
            [
                option.pop("is_correct", None)
                for option in assignment_question.get("options", [])
            ]
            for assignment_question in response_data.get("questions", [])
        ]
        return Response(response_data)

    def patch(self, request, pk):
        try:
            question = AssignmentQuestion.objects.get(pk=pk)
        except AssignmentQuestion.DoesNotExist:
            raise Http404

        serializer = AssignmentQuestionSerializer(
            question, data=request.data, partial=True, context={"request": request}
        )

        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        return Response(serializer.data)

    def delete(self, request, pk):
        try:
            question = AssignmentQuestion.objects.get(pk=pk)
        except AssignmentQuestion.DoesNotExist:
            return Response(
                {"errors": "Question Does Not Exist"}, status=status.HTTP_404_NOT_FOUND
            )
        question.delete()
        return Response(
            {"message": "Question successfully deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )


class SubmitAssignmentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, assignment_id):
        assignment = Assignment.objects.get(id=assignment_id)

        course_assignment = CourseAssignment.objects.filter(
            assignment=assignment
        ).first()
        if not course_assignment:
            return Response({"error": "Assignment not linked to a course"}, status=400)

        is_enrolled = CourseEnrollment.objects.filter(
            user=request.user, course=course_assignment.course
        ).exists()
        if not is_enrolled:
            return Response({"error": "User not enrolled in the course"}, status=403)

        if AssignmentAttempt.objects.filter(
            user=request.user, assignment=assignment
        ).exists():
            return Response(
                {"error": "You have already submitted this assignment"}, status=400
            )

        serializer = AssignmentSubmissionSerializer(
            data=request.data, context={"request": request, "assignment": assignment}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class AssignmentSubmissionReviewView(ListAPIView):
    serializer_class = AssignmentAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    @permission_required("view_assignment")
    def get_queryset(self):
        assignment_uid = self.kwargs["assignment_uid"]
        return AssignmentAttempt.objects.filter(
            assignment__uid=assignment_uid, assignment__created_by=self.request.user
        )


class MarkReviewedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @permission_required("view_assignment")
    def post(self, request, attempt_uid):
        attempt = AssignmentAttempt.objects.get(uid=attempt_uid)
        if attempt.assignment.created_by != request.user:
            return Response({"error": "Not your assignment"}, status=403)

        attempt.is_passed = request.data.get("is_passed", False)
        attempt.save()
        return Response({"message": "Marked as reviewed"})


# Create your views here.
