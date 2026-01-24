from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import RacePick, RaceResult, UserSeasonStats
from .forms import RacePickForm, SprintPickForm

# Create your views here.
@login_required
def submit_picks(request, race_id):
    race= get_object_or_404(Schedule, id=race_id)

    if timezone.now() >= race.date:
        messages.error(request, "Picks are locked for this weekend. Qualifying has already started.")
        return redirect('schedule-detail', pk=race_id)

    # Get or create picks for this race\
    race_pick, created = RacePick.objects.get_or_create(user=request.user, race=race)

    # Check if picks are locked
    if race_pick.picks_locked:
        messages.error(request, "Your picks for this race are locked and cannot be edited.")
        return redirect('my-picks')

    if request.method == 'POST':
        race_form = RacePickForm(request.POST, instance=race_pick)
        
        # Sprint Race form
        if race.sprint_race:
            sprint_form = SprintPickForm(instance=race_pick)
        else:
            sprint_form = None

    context = {
        'race': race,
        'race_form': race_form,
        'sprint_form': sprint_form,
        'is_sprint': race.sprint_race, 
        'is_edit': not created,
    }

    return render(request, 'picks/pick_form.html', context)

class MyPicksView(LoginRequiredMixin, ListView):
    """Picks History"""
    model = RacePick
    template_name = 'picks/my_picks.html'
    context_object_name = 'picks'

    def get_queryset(self):
        return RacePick.objects.filter(user=self.request.user).select_related('race')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # User's season stats
        stats, created = UserSeasonStats.objects.get_or_create(user=self.request.user)
        context['season_stats'] = stats

        # Get upcoming races where user hasn't made picks
        now = timezone.now()
        upcoming_races = Schedule.objects.filter(date__gt=now).exclude(
            picks__user=self.request.user
        ).order_by('date')
        context['upcoming_races'] = upcoming_races

        return context

class LeaderboardView(ListView):
    """Season Leaderboard"""
    model = UserSeasonStats
    template_name = 'picks/leaderboard.html'
    context_object_name = 'leaderboard'

    def get_queryset(self):
        return UserSeasonStats.objects.filter(races_participated__gt=0).select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get total number of races with results
        total_races = RaceResult.objects.filter(results_finalized=True).count()
        context['total_races'] = total_races

        # Get user's ranking if logged in
        if self.request.user.is_authenticated:
            try:
                user_stats = UserSeasonStats.objects.get(user=self.request.user)
                # Calculate rank
                better_players = UserSeasonStats.objects.filter(
                    total_points__gt=user_stats.total_points
                ).count()
                context['user_rank'] = better_players + 1
                context['user_stats'] = user_stats
            except UserSeasonStats.DoesNotExist:
                pass

        return context

class RaceResultView(DetailView):
    """View for detailed race results"""
    model = RaceResult
    template_name = 'picks/race_result.html'
    context_object_name = 'result'

    def get_object(self):
        race_id = self.kwargs.get('race_id')
        return get_object_or_404(RaceResult, race_id=race_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #Get all picks for this race
        picks =  RacePick.objects.filter(race=self.object.race).select_related('user').order_by('-points_earned')
        context['picks'] = picks

        # Get user's picks if logged in
        if self.request.user.is_authenticated:
            try:
                user_pick = RacePick.objects.get(race=self.object.race, user=self.request.user)
                context['user_pick'] = user_pick

                # Calculate user's rank for this race
                better_picks = picks.filter(points_earned__gt=user_pick.points_earned).count()
                context['user_rank'] = better_picks + 1
            except RacePick.DoesNotExist:
                pass

        return context

@login_required
def delete_pick(request, pick_id):
    """Allow user to delete a pick before lock time"""
    pick = get_object_or_404(RacePick, id=pick_id, user=request.user)

    if not pick.can_edit():
        messages.error(request, "You cannot delete picks after the deadline or once they're locked.")
        return redirect('my-picks')

    race_name = pick.race.name
    pick.delete()
    messages.success(request, f"Your picks for {race_name} have been deleted.")

    return redirect('my-picks')