from django.urls import path
from courses import views


urlpatterns = [
    path("/all", views.ListCourseView.as_view(), name="list_course"),
    path("/<uuid:uid>", views.GetDetailedCourse.as_view(), name="view_course"),
    path("/create", views.CourseView.as_view(), name="create_course"),
    path(
        "/<uuid:uid>/courses", views.CourseView.as_view(), name="update_delete_course"
    ),
    path("/<uuid:uid>/enroll", views.EnrollCourse.as_view(), name="enroll-course"),
]
