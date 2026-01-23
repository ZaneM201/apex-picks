from django import forms
from .models import RacePick
from drivers.models import Driver

class RacePickForm(forms.ModelForm):
    class Meta:
        model = RacePick
        fields = [
            'first_place', 'second_place', 'third_place',
            'pole_position', 'fastest_lap', 'driver_of_the_day',
        ]

        labels = {
            'first_place': '🥇 1st Place',
            'second_place': '🥈 2nd Place',
            'third_place': '🥉 3rd Place',
            'pole_position': '⚡ Pole Position',
            'fastest_lap': '⏱️ Fastest Lap',
            'driver_of_day': '⭐ Driver of the Day',
        }

        widgets = {
            'first_place': forms.Select(attrs={
                'class': 'form-select form-select-lg mb-3',
                'required': True
            }),
            'second_place': forms.Select(attrs={
                'class': 'form-select form-select-lg mb-3',
                'required': True
            }),
            'third_place': forms.Select(attrs={
                'class': 'form-select form-select-lg mb-3',
                'required': True
            }),
            'pole_position': forms.Select(attrs={
                'class': 'form-select mb-3',
                'required': True
            }),
            'fastest_lap': forms.Select(attrs={
                'class': 'form-select mb-3',
                'required': True
            }),
            'driver_of_day': forms.Select(attrs={
                'class': 'form-select mb-3',
                'required': True
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Order divers by number
        drivers = Driver.objects.all().order_by('number')

        for field_name in self.fields:
            self.fields[field_name].queryset = drivers
            # Custom display fomrat
            self.fields[field_name].label_from_instance = lambda obj: f"#{obj.number} - {obj.first_name} {obj.last_name} ({obj.team.name})"

    def clean(self):
        """Validate that podium picks are different drivers"""
        cleaned_data = super().clean()
        first = cleaned_data.get('first_place')
        second = cleaned_data.get('second_place')
        third = cleaned_data.get('third_place')
        
        if first and second and third:
            if len(set([first, second, third])) != 3:
                raise forms.ValidationError(
                    "You must select three different drivers for the podium positions."
                )
        
        return cleaned_data


class SprintPickForm(forms.ModelForm):
    """Additional form for sprint race picks"""
    
    class Meta:
        model = RacePick
        fields = ['sprint_first', 'sprint_second', 'sprint_third']
        
        labels = {
            'sprint_first': '🥇 Sprint 1st Place',
            'sprint_second': '🥈 Sprint 2nd Place',
            'sprint_third': '🥉 Sprint 3rd Place',
        }
        
        widgets = {
            'sprint_first': forms.Select(attrs={
                'class': 'form-select form-select-lg mb-3',
                'required': True
            }),
            'sprint_second': forms.Select(attrs={
                'class': 'form-select form-select-lg mb-3',
                'required': True
            }),
            'sprint_third': forms.Select(attrs={
                'class': 'form-select form-select-lg mb-3',
                'required': True
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        drivers = Driver.objects.all().order_by('number')
        
        for field_name in self.fields:
            self.fields[field_name].queryset = drivers
            self.fields[field_name].label_from_instance = lambda obj: f"#{obj.number} {obj.first_name} {obj.last_name} ({obj.team.name})"
    
    def clean(self):
        """Validate that sprint podium picks are different drivers"""
        cleaned_data = super().clean()
        sprint_first = cleaned_data.get('sprint_first')
        sprint_second = cleaned_data.get('sprint_second')
        sprint_third = cleaned_data.get('sprint_third')
        
        if sprint_first and sprint_second and sprint_third:
            if len(set([sprint_first, sprint_second, sprint_third])) != 3:
                raise forms.ValidationError(
                    "You must select three different drivers for the sprint podium positions."
                )
        
        return cleaned_data