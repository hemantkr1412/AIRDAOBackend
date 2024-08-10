from rest_framework import generics, status
from rest_framework.response import Response
from user.models import Account
from user.serializers import UserSerializer


class UserListCreateView(generics.ListCreateAPIView):
    queryset = Account.objects.all()
    serializer_class = UserSerializer
    

    def post(self, request, *args, **kwargs):
        account_value = request.data.get('account')

        if account_value:
            existing_account = Account.objects.filter(account=account_value).first()
            if existing_account:
                serializer = self.get_serializer(existing_account)
                return Response(serializer.data, status=status.HTTP_200_OK)
        
        # If no existing account, create a new one
        return super().post(request, *args, **kwargs)