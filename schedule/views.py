from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Schedule
from django.urls import reverse_lazy

# Create your views here.
class ScheduleListView(ListView):
    model = Schedule
    template_name = 'schedule/schedule_list.html'
    context_object_name = 'schedules'

class ScheduleDetailView(DetailView):
    model = Schedule
    template_name = 'schedule/schedule_detail.html'
    context_object_name = 'schedule'