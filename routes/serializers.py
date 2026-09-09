from rest_framework import serializers

from .models import Node, Edge


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ["id", "name"]


class EdgeSerializer(serializers.ModelSerializer):
    source = serializers.CharField()
    destination = serializers.CharField()

    class Meta:
        model = Edge
        fields = ["id", "source", "destination", "latency"]