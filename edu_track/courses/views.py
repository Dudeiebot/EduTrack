from rest_framework.generics import GenericAPIView, RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import Course, Status
from .serializers import CourseSerializer, CourseMinSerializer
from django.shortcuts import get_object_or_404
from rest_framework import permissions as django_permissions, filters as django_filters
from edu_track.backends import CustomJWTAuthentication
from django_filters import rest_framework as filters
from .permissions import IsCourseStudent, IsCourseInstructor
from base.permissions import permission_required


class ListCourseView(ListAPIView):
    serializer_class = CourseMinSerializer
    queryset = Course.objects.filter(publish_status=Status.PUBLISHED)
    authentication_classes = []
    permission_classes = [django_permissions.AllowAny]
    authentication_classes = [CustomJWTAuthentication]
    filter_backends = [django_filters.SearchFilter, filters.DjangoFilterBackend]
    search_fields = ["@title", "@description"]
    ordering_fields = "__all__"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CourseView(GenericAPIView):

    serializer_class = CourseSerializer
    permission_classes = [
        django_permissions.IsAuthenticated,
    ]

    def get_object(self):
        return get_object_or_404(Course, pk=self.kwargs.get("pk"))

    @permission_required("create_course")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @permission_required("update_course")
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @permission_required("delete_course")
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetDetailedCourse(RetrieveAPIView):
    serializer_class = CourseSerializer
    permission_classes = [
        django_permissions.IsAuthenticated,
        IsCourseStudent,
        IsCourseInstructor,
    ]
    queryset = Course.objects.filter(publish_status=Status.PUBLISHED)
    lookup_field = "uid"
    lookup_url_kwarg = "uid"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class EnrollCourse(GenericAPIView):
    permission_classes = [
        django_permissions.IsAuthenticated,
    ]

    def get_object(self):
        return get_object_or_404(Course, pk=self.kwargs.get("pk"))

    def post(self, request, *args, **kwargs):
        course = self.get_object()
        course.enrol_user(request.user)
        return Response({"detail": "Enrolled successfully."}, status=status.HTTP_200_OK)


# Create your views here.
