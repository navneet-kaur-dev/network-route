from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Node, Edge, RouteHistory
from .serializers import NodeSerializer, EdgeSerializer


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

class ShortestPathView(APIView):

    def post(self, request):
        source_name = request.data.get("source")
        destination_name = request.data.get("destination")

        if not source_name or not destination_name:
            return Response(
                {"error": "Source and destination are required"},
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

        edges = Edge.objects.all()

        graph = {}

        for node in Node.objects.all():
            graph[node.name] = []

        for edge in edges:
            graph[edge.source.name].append(
                (edge.destination.name, edge.latency)
            )

        distances = {}

        for node in graph:
            distances[node] = float("inf")

        distances[source.name] = 0

        previous = {}
        unvisited = set(graph.keys())

        while unvisited:
            current = min(
                unvisited,
                key=lambda node: distances[node]
            )

            if distances[current] == float("inf"):
                break

            unvisited.remove(current)

            if current == destination.name:
                break

            for neighbor, latency in graph[current]:
                new_distance = distances[current] + latency

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current

        if distances[destination.name] == float("inf"):
            return Response(
                {
                    "error": f"No path exists between {source.name} and {destination.name}"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        path = []
        current = destination.name

        while current:
            path.append(current)
            current = previous.get(current)

        path.reverse()

        RouteHistory.objects.create(
            source=source.name,
            destination=destination.name,
            total_latency=distances[destination.name],
            path=path
        )

        return Response(
            {
                "total_latency": distances[destination.name],
                "path": path
            },
            status=status.HTTP_200_OK
        )

class RouteHistoryView(APIView):

    def get(self, request):
        history = RouteHistory.objects.all().order_by("-created_at")

        source = request.query_params.get("source")
        destination = request.query_params.get("destination")
        limit = request.query_params.get("limit")
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        if source:
            history = history.filter(source=source)

        if destination:
            history = history.filter(destination=destination)

        if date_from:
            history = history.filter(created_at__gte=date_from)

        if date_to:
            history = history.filter(created_at__lte=date_to)

        if limit:
            history = history[:int(limit)]

        data = []

        for route in history:
            data.append({
                "id": route.id,
                "source": route.source,
                "destination": route.destination,
                "total_latency": route.total_latency,
                "path": route.path,
                "created_at": route.created_at
            })

        return Response(data, status=status.HTTP_200_OK)