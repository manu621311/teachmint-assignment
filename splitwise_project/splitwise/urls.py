from django.urls import path
from .views import SplitWiseView

appname = 'splitwise'

urlpatterns = [
    path("splitwise", SplitWiseView.as_view()),
]
