from rest_framework.permissions import BasePermission


class IsCourseStudent(BasePermission):
    def has_object_permission(self, request, view, instance):
        return instance.students.filter(user=request.user).exists()


class IsCourseInstructor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user
