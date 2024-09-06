from rest_framework import generics, pagination, status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.db.models import Sum
import requests
from decimal import Decimal
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

        return Vote.objects.filter(account=account).order_by("-created_at")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"error": "No votes found for the user."},
                status=status.HTTP_404_NOT_FOUND,
            )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class WinningVotesListView(generics.ListAPIView):
    serializer_class = MyPredictionsSerializer

    def get_queryset(self):
        account_address = self.request.query_params.get("wallet_address")

        if not account_address:
            raise ValidationError("The 'account' query parameter is required.")

        account = Account.objects.filter(account=account_address).first()
        if not account:
            raise ValidationError("Account not found.")

        votes = Vote.objects.filter(account=account).order_by("-created_at")

        # Filter out votes that are not winning
        winning_votes = [
            vote
            for vote in votes
            if vote.possible_result == vote.possible_result.event.final_result
        ]
        return winning_votes


@api_view(["POST"])
def claim_reward(request):
    try:
        vote_id = request.data.get("vote_id")
        account_address = request.data.get("account")
        vote = Vote.objects.get(id=vote_id, account__account=account_address)

        # First layer security check:
        if vote.is_claimed:
            return Response(
                {"error": "Already claimed"}, status=status.HTTP_400_BAD_REQUEST
            )

        if vote.amount_rewarded is None or vote.amount_rewarded == 0:
            return Response(
                {"error": "No reward available to claim"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Call the claim_amount function to interact with the smart contract
        tx_hash = claim_amount(vote.amount_rewarded, vote.account.account)
        if tx_hash:
            vote.tx_hash = tx_hash
            vote.is_claimed = True
            vote.save(update_fields=["tx_hash", "is_claimed"])
            return Response(
                {"message": "Reward claimed successfully", "tx_hash": tx_hash},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Failed to claim the reward"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    except Vote.DoesNotExist:
        return Response({"error": "Vote not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class KPIView(APIView):
    COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"
    AMB_TOKEN_ID = "amber"
    def get_token_price(self):
        """Fetch AMB token price in USD from CoinGecko API."""
        params = {"ids": self.AMB_TOKEN_ID, "vs_currencies": "usd"}
        API_KEY = "CG-rv9LZaiQs56cYhmh2jShDDuQ"
        headers = {"Authorization": f"Bearer {API_KEY}"}
        try:
            response = requests.get(
                self.COINGECKO_API_URL, params=params, headers=headers
            )
            response_data = response.json()
            print(response_data)
            return Decimal(response_data[self.AMB_TOKEN_ID]["usd"])
        except (requests.RequestException, KeyError, ValueError) as e:
            print("Exception raised while fetching token price:", e)
            return None
    def get(self, request):
        # Fetch the AMB token price in USD
        amb_token_price = self.get_token_price()
        print(amb_token_price)
        if amb_token_price is None:
            return Response(
                {"error": "Failed to fetch AMB token price"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        # Calculate the KPIs
        total_volume_locked = (
            Event.objects.aggregate(total_volume=Sum("token_volume"))["total_volume"]
            or 0
        )
        total_platform_fee = (
            Event.objects.aggregate(total_fee=Sum("platform_share"))["total_fee"] or 0
        )
        total_burn_fee = (
            Event.objects.aggregate(total_burn=Sum("burn_share"))["total_burn"] or 0
        )
        # Convert token values to USD using the fetched AMB token price
        total_volume_locked_in_usd = total_volume_locked * amb_token_price
        total_platform_fee_in_usd = total_platform_fee * amb_token_price
        total_burn_fee_in_usd = total_burn_fee * amb_token_price
        # Serialize and round the data for better precision
        data = {
            "total_volume_locked": round(total_volume_locked_in_usd, 2),
            "total_platform_fee": round(total_platform_fee_in_usd, 2),
            "total_burn_fee": round(total_burn_fee_in_usd, 2),
        }
        return Response(data, status=status.HTTP_200_OK)

















