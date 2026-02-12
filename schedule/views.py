from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Schedule
from django.urls import reverse_lazy

# Create your views here.
class ScheduleListView(ListView):
    model = Schedule
    template_name = 'schedule/schedule_list.html'
    context_object_name = 'schedules'

    def get_queryset(self):
        return (
            Schedule.objects.filter(date__year=2026).order_by('date')
        )

class ScheduleDetailView(DetailView):
    model = Schedule
    template_name = 'schedule/schedule_detail.html'
    context_object_name = 'schedule'