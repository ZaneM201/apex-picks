from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.shortcuts import redirect

# Create your views here.
class UserLoginView(LoginView):
    template_name = 'users/login.html'

def logout_view(request):
    logout(request)
    return redirect('login')