from django.urls import path
from .views import NodeView, EdgeView, ShortestPathView, RouteHistoryView


urlpatterns = [
    path("nodes", NodeView.as_view()),
    path("edges", EdgeView.as_view()),
    path("routes/shortest", ShortestPathView.as_view()),
    path("routes/history", RouteHistoryView.as_view()),

]