from rest_framework import generics, pagination, status
from rest_framework.response import Response
from .models import Event, Vote, Category
from user.models import Account
from .serializers import (
    EventSerializer,
    VoteSerializer,
    CategorySerializer,
    MyPredictionsSerializer,
)


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

        return Vote.objects.filter(account=account)

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
