from rest_framework import serializers
from .models import Role, PlatformActors


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"

    isDisabled = serializers.BooleanField(default=False, required=False)
    isDeleted = serializers.BooleanField(default=False, required=False)
    createdBy = serializers.IntegerField(required=False, allow_null=True)
    createdByCategory = serializers.ChoiceField(
        choices=[(tag.value, tag.name) for tag in PlatformActors], required=False
    )
    deletedAt = serializers.DateTimeField(required=False, allow_null=True)

    def create(self, validated_data):
        createdBy = self.context.get("createdBy")
        validated_data["createdBy"] = createdBy
        validated_data["createdByCategory"] = "USER"
        return Role.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)

        instance.save()
        return instance
