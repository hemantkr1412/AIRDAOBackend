from django.urls import path
from user.views import UserListCreateView

urlpatterns = [
    path("account/",UserListCreateView.as_view(), name="user-list-create"),
]


