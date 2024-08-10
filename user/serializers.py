from rest_framework import serializers
from user.models import Account


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"