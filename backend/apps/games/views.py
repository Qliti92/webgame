from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Game, GamePackage
from .serializers import GameListSerializer, GameDetailSerializer


class GameListView(generics.ListAPIView):
    """API endpoint for listing games"""
    queryset = Game.objects.filter(status='active')
    serializer_class = GameListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['display_order', 'created_at', 'name']
    ordering = ['display_order']


class GameDetailView(generics.RetrieveAPIView):
    """API endpoint for game detail"""
    queryset = Game.objects.all()
    serializer_class = GameDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
