from django.urls import path
from . import views

urlpatterns = [
    path('submit/<int:race_id>/', views.submit_picks, name='submit-picks'),
    path('my-picks/', views.MyPicksView.as_view(), name='my-picks'),
    path('delete/<int:pick_id>/', views.delete_pick, name='delete-pick'),    
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
    path('results/<int:race_id>/', views.RaceResultView.as_view(), name='race-results'),
]