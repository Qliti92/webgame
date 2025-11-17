from django.urls import path
from .views import GameListView, GameDetailView

app_name = 'games'

urlpatterns = [
    path('', GameListView.as_view(), name='game_list'),
    path('<slug:slug>/', GameDetailView.as_view(), name='game_detail'),
]
