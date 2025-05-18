from rest_framework import serializers
from .models import (
    Assignment,
    AssignmentQuestion,
    AssignmentQuestionOption,
    AssignmentAttempt,
    UserQuestionResponse,
)


class AssignmentQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentQuestionOption
        fields = ["text", "is_correct"]


class AssignmentQuestionSerializer(serializers.ModelSerializer):
    options = AssignmentQuestionOptionSerializer(many=True, source="assignment_options")

    class Meta:
        model = AssignmentQuestion
        fields = [
            "uid",
            "text",
            "options",
        ]

    def update(self, instance, validated_data):
        instance.text = validated_data.get("text", instance.text)
        instance.save()

        options_data = validated_data.pop("assignment_options", [])
        for option_data in options_data:
            uid = option_data.get("uid")
            if uid:
                try:
                    option = AssignmentQuestionOption.objects.get(
                        uid=uid, question=instance
                    )
                    for key, value in option_data.items():
                        setattr(option, key, value)
                    option.save()
                except AssignmentQuestionOption.DoesNotExist:
                    AssignmentQuestionOption.objects.create(
                        question=instance, **option_data
                    )

        return instance


class AssignmentWithQuestionsSerializer(serializers.ModelSerializer):
    assignment_question = AssignmentQuestionSerializer(many=True)

    class Meta:
        model = Assignment
        fields = [
            "title",
            "description",
            "cover_image",
            "duration",
            "deadline",
            "allowed_attempts",
            "assignment_question",
        ]

    def validate_course(self, value):
        user = self.context["request"].user
        if value.created_by != user:
            raise serializers.ValidationError("You are not the creator of this course.")
        return value

    def create(self, validated_data):
        questions_data = validated_data.pop("assignment_question")
        assignment = Assignment.objects.create(
            **validated_data, created_by=self.context["request"].user
        )

        for question_data in questions_data:
            options_data = question_data.pop("assignment_options")
            question = AssignmentQuestion.objects.create(
                assignment=assignment, **question_data
            )
            for option_data in options_data:
                AssignmentQuestionOption.objects.create(
                    question=question, **option_data
                )

        return assignment


class AnswerSerializer(serializers.Serializer):
    question_uid = serializers.UUIDField()
    option_uid = serializers.UUIDField()


class AssignmentSerializer(serializers.ModelSerializer):
    answers = serializers.ListField(child=AnswerSerializer(many=False))

    class Meta:
        model = Assignment
        fields = "__all__"


class AssignmentSubmissionSerializer(serializers.Serializer):
    answers = serializers.ListField(child=AnswerSerializer(many=False))

    def create(self, validated_data):
        user = self.context["request"].user
        assignment = self.context["assignment"]
        responses_data = validated_data["answers"]

        attempt = AssignmentAttempt.objects.create(user=user, assignment=assignment)
        correct_count = 0
        total = 0

        for item in responses_data:
            question_uid = item["question"]
            option_uid = item["selected_option"]
            question = AssignmentQuestion.objects.get(uid=question_uid)
            selected = AssignmentQuestionOption.objects.get(uid=option_uid)
            is_correct = selected.is_correct
            if is_correct:
                correct_count += 1
            total += 1
            UserQuestionResponse.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected,
                is_correct=is_correct,
            )

        score = (correct_count / total) * 100
        attempt.score = score
        attempt.save()
        return attempt


class AssignmentAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentAttempt
        fields = "__all__"
