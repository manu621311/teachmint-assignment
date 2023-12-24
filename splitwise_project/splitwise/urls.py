from django.urls import path
from .views import SplitWiseView, SimplifySplitView

appname = 'splitwise'

urlpatterns = [
    path("splitwise", SplitWiseView.as_view()),         #Url for expense and its splitting
    path("splitwise/simplify", SimplifySplitView.as_view()),    #Url for simplifying split
]
