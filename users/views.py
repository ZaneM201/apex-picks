from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import UpdateView, DetailView
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from .forms import UserRegisterForm, ProfileForm
from .models import Profile


# Create your views here.

# Login View
class UserLoginView(LoginView):
    template_name = 'users/login.html'

def logout_view(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            Profile.objects.create(user=user, phone_number='', zip_code='')
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

# Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html' 

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "users/profile_update.html"
    success_url = reverse_lazy("profile_details")

    def get_object(self):
        # Get or create profile for current user
        profile, created = Profile.objects.get_or_create(
            user=self.request.user,
            defaults={'phone_number': '', 'zip_code': ''}
        )
        return profile

class ProfileDetailsView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "users/profile_details.html"
    context_object_name = 'profile_user'
    
    def get_object(self):
        # If username provided in URL, show that user's profile
        username = self.kwargs.get('username')
        if username:
            return get_object_or_404(User, username=username)
        # Otherwise show logged-in user's profile
        return self.request.user
    
    def get_context_data(self, **kwargs):
        from picks.models import RacePick, UserSeasonStats, RaceResult
        
        context = super().get_context_data(**kwargs)
        profile_user = self.get_object()
        
        # Get or create profile
        profile, created = Profile.objects.get_or_create(
            user=profile_user,
            defaults={'phone_number': '', 'zip_code': ''}
        )
        context['profile'] = profile
        
        # Get season stats
        season_stats, created = UserSeasonStats.objects.get_or_create(
            user=profile_user,
            defaults={
                'total_points': 0,
                'correct_poles': 0,
                'correct_wins': 0,
                'races_participated': 0
            }
        )
        context['season_stats'] = season_stats
        
        # Calculate user's ranking
        if season_stats.races_participated > 0:
            better_players = UserSeasonStats.objects.filter(
                total_points__gt=season_stats.total_points
            ).count()
            context['user_rank'] = better_players + 1
            
            total_players = UserSeasonStats.objects.filter(
                races_participated__gt=0
            ).count()
            context['total_players'] = total_players
        
        # Get user's picks (recent first)
        user_picks = (
            RacePick.objects.filter(user=profile_user)
            .select_related('race')
            .order_by('-race__date')[:10]
        )
        context['recent_picks'] = user_picks

        # Calculate additional stats
        if user_picks.exists():
            # Average points per race (on recent picks)
            avg_points = user_picks.aggregate(Avg('points_earned'))['points_earned__avg']
            context['avg_points_per_race'] = round(avg_points, 1) if avg_points else 0
            
            # Best race (highest points)
            best_race = (
                RacePick.objects.filter(user=profile_user)
                .order_by('-points_earned')
                .first
            )
            context['best_race'] = best_race
            
            # Count podium predictions (any position correct)
            podium_correct = 0
            for pick in user_picks:
                try:
                    result = pick.race.result
                except RacePick.DoesNotExist:
                    continue

                if (
                    pick.first_place == result.first_palce
                    or pick.second_place == result.second_place
                    or pick.third_place == result.third_place
                ):
                    podium_correct +=1
                
            context['podium_predictions'] = podium_correct
            
            # Accuracy percentages
            if season_stats.races_participated > 0:
                context['win_accuracy'] = round(
                    (season_stats.correct_wins / season_stats.races_participated) * 100, 1
                )
                context['pole_accuracy'] = round(
                    (season_stats.correct_poles / season_stats.races_participated) * 100, 1
                )
        
        # Check if viewing own profile
        context['is_own_profile'] = (self.request.user == profile_user)
        
        return context