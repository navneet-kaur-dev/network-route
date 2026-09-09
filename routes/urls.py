from django.urls import path
from .views import NodeView, EdgeView


urlpatterns = [
    path("nodes", NodeView.as_view()),
    path("edges", EdgeView.as_view()),

]