from rest_framework import generics
from user.models import Account
from user.serializers import UserSerializer


class UserListCreateView(generics.ListCreateAPIView):
    queryset = Account.objects.all()
    serializer_class = UserSerializer
    