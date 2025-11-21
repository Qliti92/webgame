from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Game, GamePackage
from .serializers import GameListSerializer, GameDetailSerializer, GamePackageSerializer


class GameListView(generics.ListAPIView):
    """API endpoint for listing games"""
    queryset = Game.objects.filter(status='active')
    serializer_class = GameListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['display_order', 'created_at', 'name']
    ordering = ['display_order']

    def get_serializer_context(self):
        """Pass request context to serializer"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class GameDetailView(generics.RetrieveAPIView):
    """API endpoint for game detail"""
    queryset = Game.objects.all()
    serializer_class = GameDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_serializer_context(self):
        """Pass request context to serializer"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class GamePackagesView(APIView):
    """
    API endpoint to get packages for a specific game, grouped by type.

    Returns packages separated into normal and warranty categories.
    Example: GET /api/games/{game_id}/packages/ or /api/games/{slug}/packages/
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, game_identifier):
        """Get packages for a game, grouped by type"""
        # Try to get game by ID or slug
        try:
            if game_identifier.isdigit():
                game = Game.objects.get(id=game_identifier, status='active')
            else:
                game = Game.objects.get(slug=game_identifier, status='active')
        except Game.DoesNotExist:
            return Response(
                {'error': 'Game not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get all active packages for this game
        all_packages = GamePackage.objects.filter(
            game=game,
            is_active=True
        ).order_by('display_order', 'price_usd')

        # Separate into normal and warranty packages
        normal_packages = all_packages.filter(package_type='normal')
        warranty_packages = all_packages.filter(package_type='warranty')

        # Serialize
        normal_serializer = GamePackageSerializer(normal_packages, many=True, context={'request': request})
        warranty_serializer = GamePackageSerializer(warranty_packages, many=True, context={'request': request})

        return Response({
            'game': {
                'id': game.id,
                'name': game.name,
                'slug': game.slug,
            },
            'packages': {
                'normal': normal_serializer.data,
                'warranty': warranty_serializer.data,
            }
        })
