from django.urls import path
from .views import UsersView

appname = 'users'

urlpatterns = [
    path("users", UsersView.as_view()),
]
