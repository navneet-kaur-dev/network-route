from django.urls import path
from .views import NodeView


urlpatterns = [
    path("nodes", NodeView.as_view()),
]