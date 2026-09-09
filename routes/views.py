from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Node
from .serializers import NodeSerializer


class NodeView(APIView):

    def post(self, request):
        serializer = NodeSerializer(data=request.data)

        if serializer.is_valid():
            node = serializer.save()

            return Response(
                {
                    "id": node.id,
                    "name": node.name
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
        
class EdgeView(APIView):

    def post(self, request):
        serializer = EdgeSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        source_name = serializer.validated_data["source"]
        destination_name = serializer.validated_data["destination"]
        latency = serializer.validated_data["latency"]

        if latency <= 0:
            return Response(
                {"error": "Latency must be greater than 0"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            source = Node.objects.get(name=source_name)
            destination = Node.objects.get(name=destination_name)
        except Node.DoesNotExist:
            return Response(
                {"error": "Source or destination node not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Edge.objects.filter(
            source=source,
            destination=destination
        ).exists():
            return Response(
                {"error": "Edge already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        edge = Edge.objects.create(
            source=source,
            destination=destination,
            latency=latency
        )

        return Response(
            {
                "id": edge.id,
                "source": source.name,
                "destination": destination.name,
                "latency": edge.latency
            },
            status=status.HTTP_201_CREATED
        )