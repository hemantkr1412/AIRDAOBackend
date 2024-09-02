from rest_framework import generics, pagination, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Event, Vote, Category
from user.models import Account
from .serializers import (
    EventSerializer,
    VoteSerializer,
    CategorySerializer,
    MyPredictionsSerializer,
)
from event.contract_call import claim_amount
from rest_framework.exceptions import ValidationError

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class EventDetailView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class EventListView(generics.ListAPIView):
    queryset = Event.objects.select_related("category").prefetch_related(
        "possible_results"
    )
    serializer_class = EventSerializer
    pagination_class = pagination.PageNumberPagination


class EventListSortView(generics.ListAPIView):
    serializer_class = EventSerializer
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        queryset = Event.objects.select_related("category").prefetch_related(
            "possible_results"
        )
        sort_by = self.request.query_params.get("sort_by", None)

        if sort_by == "new":
            queryset = queryset.order_by("-start_date")
        elif sort_by == "ending_soon":
            queryset = queryset.order_by("end_date")
        elif sort_by == "volume":
            queryset = queryset.order_by(
                "-token_volume"
            )  # Sorting by token volume in descending order
        return queryset


class VoteCreateView(generics.CreateAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VoteListView(generics.ListAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer


class VoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer


class MyPredictionsListView(generics.ListAPIView):
    serializer_class = MyPredictionsSerializer
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        # Retrieve the wallet address from the request headers
        wallet_address = self.request.query_params.get("wallet_address")

        if not wallet_address:
            return Vote.objects.none()

        account = Account.objects.filter(account=wallet_address).first()

        if not account:
            return Vote.objects.none()

        return Vote.objects.filter(account=account).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"error": "No votes found for the user."}, status=status.HTTP_404_NOT_FOUND)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class WinningVotesListView(generics.ListAPIView):
    serializer_class = MyPredictionsSerializer
    def get_queryset(self):
<<<<<<< HEAD
        account_address = self.request.query_params.get('wallet_address')
        if not account_address:
            raise ValidationError("The 'account' query parameter is required.")
        account = Account.objects.filter(account=account_address).first()
        if not account:
            raise ValidationError("Account not found.")
        votes = Vote.objects.filter(account=account).order_by('-created_at')
=======
        account_address = self.request.query_params.get('account')

        if not account_address:
            raise ValidationError("The 'account' query parameter is required.")

        account = Account.objects.filter(account=account_address).first()
        if not account:
            raise ValidationError("Account not found.")

        votes = Vote.objects.filter(account=account).order_by('-created_at')

>>>>>>> 1f1857ef33e077c83f36836ff8af5191ec2a299d
        # Filter out votes that are not winning
        winning_votes = [
            vote for vote in votes if vote.possible_result == vote.possible_result.event.final_result
        ]
<<<<<<< HEAD
=======

>>>>>>> 1f1857ef33e077c83f36836ff8af5191ec2a299d
        return winning_votes


@api_view(['POST'])
def claim_reward(request):
    try:
        vote_id = request.data.get('vote_id')
        account_address = request.data.get('account')
        vote = Vote.objects.get(id=vote_id, account__account=account_address)

        if vote.amount_rewarded is None or vote.amount_rewarded == 0:
            return Response({"error": "No reward available to claim"}, status=status.HTTP_400_BAD_REQUEST)

        # Call the claim_amount function to interact with the smart contract
        tx_hash = claim_amount(float(vote.amount_rewarded), vote.account.account)

        if tx_hash:
            vote.tx_hash = tx_hash
            vote.save(update_fields=["tx_hash"])
            return Response({"message": "Reward claimed successfully", "tx_hash": tx_hash}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to claim the reward"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Vote.DoesNotExist:
        return Response({"error": "Vote not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)