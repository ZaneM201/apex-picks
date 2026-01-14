from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView
from .models import Driver, Team
from .forms import DriverForm
from django.urls import reverse_lazy

# Create your views here.
class TeamListView(ListView):
    model = Team
    template_name = "team/team_list.html"

class DriverCreateView(CreateView):
    model = Driver
    template_name = "driver/driver_form.html"
    form_class = DriverForm
    success_url = reverse_lazy("team-list")

class TeamDetailView(DetailView):
    model = Team
    template_name = "team/team_detail.html"
