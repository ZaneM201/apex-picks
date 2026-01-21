from django.shortcuts import render, redirect, HttpResponse
from datetime import datetime 
from schedule.models import Schedule
from .forms import ContactForm

# Create your views here.
def home_view(request):
    # Get the next upcoming race (using now for DateTimeField comparison)
    now = datetime.now()
    next_race = Schedule.objects.filter(date__gte=now).order_by('date').first()  # AND THIS LINE
    
    # Debug: Show all races if no upcoming race found
    if not next_race:
        # Fallback to show the first race regardless of date (for testing)
        next_race = Schedule.objects.order_by('date').first()
    
    context = {
        'next_race': next_race
    }
    return render(request, 'pages/home.html', context)

def about_view(request):
    return render(request, 'pages/about.html')

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process form data 
            pass
            return redirect('success')
    else:
        form = ContactForm()
    return render(request, 'pages/contact.html', {'form': form})

def success_view(request):
    return HttpResponse("Thank you for your message. We will get back to you soon.")