from django.urls import path
from .views import (
    EventDetailView,
    EventListView,
    VoteListView,
    VoteCreateView,
    VoteDetailView,
)

urlpatterns = [
    path("", EventListView.as_view(), name="event-list"),
    path("<int:pk>/", EventDetailView.as_view(), name="event-detail"),
    path("votes/", VoteListView.as_view(), name="vote-list"),
    path("votes/create/", VoteCreateView.as_view(), name="vote-create"),
    path("votes/<int:pk>/", VoteDetailView.as_view(), name="vote-detail"),
]
