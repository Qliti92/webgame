from django.urls import path
from .views import GameListView, GameDetailView, GamePackagesView

app_name = 'games'

urlpatterns = [
    path('', GameListView.as_view(), name='game_list'),
    path('<str:game_identifier>/packages/', GamePackagesView.as_view(), name='game_packages'),
    path('<slug:slug>/', GameDetailView.as_view(), name='game_detail'),
]
