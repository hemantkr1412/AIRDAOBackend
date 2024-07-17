from rest_framework import serializers
from .models import Category, Event, PossibleResult, Vote
from user.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class PossibleResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = PossibleResult
        fields = ["id", "result"]


class EventSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    possible_results = PossibleResultSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "category",
            "event_name",
            "avatar",
            "market",
            "start_date",
            "end_date",
            "resolution_date",
            "token_volume",
            "possible_results",
        ]

    def validate(self, data):
        if data["start_date"] >= data["end_date"]:
            raise serializers.ValidationError("End date should be after start date")
        if data["resolution_date"] <= data["end_date"]:
            raise serializers.ValidationError(
                "Resolution date should be after end date"
            )
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["account"]


class VoteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user", write_only=True
    )

    class Meta:
        model = Vote
        fields = ["user", "user_id", "possible_result"]

    def validate(self, data):
        user = self.context["request"].user
        possible_result = data["possible_result"]

        # Check if the user has already voted for the possible_result
        if Vote.objects.filter(user=user, possible_result=possible_result).exists():
            raise serializers.ValidationError(
                "You have already voted for this possible result."
            )

        # Assuming you have some validation for checking if the possible_result is valid
        if not PossibleResult.objects.filter(id=possible_result.id).exists():
            raise serializers.ValidationError("Invalid possible result.")

        return data

    def create(self, validated_data):
        user = self.context["request"].user
        vote = Vote.objects.create(user=user, **validated_data)
        return vote
