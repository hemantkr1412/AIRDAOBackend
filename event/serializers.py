from rest_framework import serializers
from .models import Category, Event, PossibleResult, Vote
from user.models import Account
from collections import defaultdict
from django.db.models import F
from django.db import models


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class PossibleResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = PossibleResult
        fields = ["id", "result"]

class VoteSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all()
    )
    possible_result = serializers.PrimaryKeyRelatedField(
        queryset=PossibleResult.objects.all()
    )

    class Meta:
        model = Vote
        fields = ["account", "possible_result", "token_staked", "tx_hash", "amount_rewarded"]

    def create(self, validated_data):
        token_staked = validated_data.get("token_staked", 0)
        possible_result = validated_data["possible_result"]
        event = possible_result.event

        # Check if token_staked meets the min_token_stake requirement
        if token_staked < event.min_token_stake:
            raise serializers.ValidationError(
                f"Token stake must be at least {event.min_token_stake}."
            )
        vote = Vote.objects.create(**validated_data)

        # Increment the token volume of the related event
        if event.token_volume is None:
            event.token_volume = 0
        event.token_volume += token_staked
        event.save(update_fields=['token_volume'])

        return vote


class EventSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    # possible_results = PossibleResultSerializer(many=True, read_only=True)
    possible_results = serializers.SerializerMethodField() 
    # event_votes = serializers.SerializerMethodField()
    # print(event_votes)

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
       


    def get_possible_results(self, obj):
        # Get the serialized possible results
        possible_results = PossibleResultSerializer(obj.possible_results.all(), many=True).data

        # Calculate the total tokens staked for the event
        total_staked = Vote.objects.filter(possible_result__event=obj).aggregate(total=models.Sum('token_staked'))['total'] or 0

        # Calculate and add percentage to each possible result
        for result in possible_results:
            result_id = result['id']
            total_for_result = Vote.objects.filter(possible_result__id=result_id).aggregate(total=models.Sum('token_staked'))['total'] or 0
            percentage = (total_for_result / total_staked) * 100 if total_staked > 0 else 0
            result['percentage'] = round(percentage, 2)  # Add the percentage field

        return possible_results

    def validate(self, data):
        if data["start_date"] >= data["end_date"]:
            raise serializers.ValidationError("End date should be after start date")
        if data["resolution_date"] <= data["end_date"]:
            raise serializers.ValidationError(
                "Resolution date should be after end date"
            )
        return data


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id","account"]


class VoteSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all()
    )
    possible_result = serializers.PrimaryKeyRelatedField(
        queryset=PossibleResult.objects.all()
    )

    class Meta:
        model = Vote
        fields = ["account", "possible_result", "token_staked", "tx_hash", "amount_rewarded"]

    def create(self, validated_data):
        token_staked = validated_data.get("token_staked", 0)
        possible_result = validated_data["possible_result"]
        event = possible_result.event

        # Check if token_staked meets the min_token_stake requirement
        if token_staked < event.min_token_stake:
            raise serializers.ValidationError(
                f"Token stake must be at least {event.min_token_stake}."
            )
        vote = Vote.objects.create(**validated_data)

        # Increment the token volume of the related event
        if event.token_volume is None:
            event.token_volume = 0
        event.token_volume += token_staked
        event.save(update_fields=['token_volume'])

        return vote


class MyPredictionsSerializer(serializers.ModelSerializer):
    event_id = serializers.CharField(source="possible_result.event.id",read_only=True)
    event_name = serializers.CharField(
        source="possible_result.event.event_name", read_only=True
    )
    result = serializers.CharField(source="possible_result.result", read_only=True)
    amount_rewarded = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Vote
        fields = ['id','tx_hash','event_id', 'event_name', 'result', 'token_staked', 'amount_rewarded', 'created_at','is_claimed']
