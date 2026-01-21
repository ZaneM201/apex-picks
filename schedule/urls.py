from django.urls import path
from . import views

urlpatterns = [
    path('2026/', views.ScheduleListView.as_view(), name='schedule-list'),
    path('2026/<int:pk>/', views.ScheduleDetailView.as_view(), name='schedule-detail'),
]