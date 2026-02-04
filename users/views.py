from django.shortcuts import render, redirect
from django.views.generic import UpdateView, DetailView
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse_lazy
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
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

    Profile.objects.create(user=user)

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

class ProfileUpdateView(UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'users/profile_update.html'
    success_url = reverse_lazy('home') # should redirect to profile view

    def get_object(self):
        # Reads the record (that will be modified) from db
        profile = Profile.objects.get(user=self.request.user)
        return profile

class ProfileDetails(DetailView):
    model = Profile
    template_name = 'users/profile_details.html'
