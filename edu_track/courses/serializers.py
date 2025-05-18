from rest_framework import serializers
from .models import Course


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = (
            "uid",
            "title",
            "description",
            "publish_status",
            "content_url",
            "content_type",
            "metadata",
            "cover_image",
            "duration",
            "is_open_for_enrollment",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "uid",
            "created_by",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {
            "cover_image": {"required": False},
        }

    def create(self, validated_data):
        _user = self.context["request"].user
        validated_data["created_by"] = _user
        _course = super().create(validated_data)

        return _course

    def update(self, instance, validated_data):
        _course = super().update(instance, validated_data)


class CourseMinSerializer(serializers.ModelSerializer):
    students_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "uid",
            "title",
            "description",
            "publish_status",
            "cover_image",
            "duration",
            "is_open_for_enrollment",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "uid",
            "created_by",
            "created_at",
            "updated_at",
        )

    def get_students_count(self, instance):
        return instance.students.count()
