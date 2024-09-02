from django.urls import path
from .views import (
    CategoryListView,
    EventDetailView,
    EventListSortView,
    EventListView,
    VoteListView,
    VoteCreateView,
    VoteDetailView,
    MyPredictionsListView,
    WinningVotesListView,
    claim_reward,
)
from .contract_call import (
    # create_event_view,
    # update_event,
    # close_event,
    claim_amount,
    check_contract_balance,
    change_owner,
    get_outcome_info,
    get_user_prediction,
    get_owner,
)

urlpatterns = [
    path("", EventListView.as_view(), name="event-list"),
    path("sorted-event", EventListSortView.as_view(), name="event-sorted-list"),
    path("<int:pk>/", EventDetailView.as_view(), name="event-detail"),
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("votes/", VoteListView.as_view(), name="vote-list"),
    path("votes/create/", VoteCreateView.as_view(), name="vote-create"),
    path("votes/<int:pk>/", VoteDetailView.as_view(), name="vote-detail"),
    path("my-predictions/", MyPredictionsListView.as_view(), name="my-predicitons"),
    path('winning-votes/', WinningVotesListView.as_view(), name='winning-votes'),
    path("claim-reward/", claim_reward, name="claim-reward"),
    # path("create-event/", create_event_view, name="create_event"),
    # path("update_event/<int:event_id>/", update_event),
    # path("close_event/<int:event_id>/<int:outcome_id>/", close_event),
    # path("claim_amount/", claim_amount),
    path("check_contract_balance/", check_contract_balance),
    path("change_owner/", change_owner),
    path("get_outcome_info/<int:event_id>/", get_outcome_info),
    path(
        "get_user_prediction/<int:event_id>/<int:outcome_id>/<str:user_address>/",
        get_user_prediction,
    ),
    path("get_owner/", get_owner),
]
