from django.db import models


class Node(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Edge(models.Model):
    source = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="outgoing_edges"
    )
    destination = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="incoming_edges"
    )
    latency = models.FloatField()

    def __str__(self):
        return f"{self.source} -> {self.destination}"