from django.urls import path
from .views import (
    CategoryListView,
    EventDetailView,
    EventListSortView,
    EventListView,
    VoteListView,
    VoteCreateView,
    VoteDetailView,
)

urlpatterns = [
    path("", EventListView.as_view(), name="event-list"),
    path("sorted-event", EventListSortView.as_view(), name="event-sorted-list"),
    path("<int:pk>/", EventDetailView.as_view(), name="event-detail"),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path("votes/", VoteListView.as_view(), name="vote-list"),
    path("votes/create/", VoteCreateView.as_view(), name="vote-create"),
    path("votes/<int:pk>/", VoteDetailView.as_view(), name="vote-detail"),
]
