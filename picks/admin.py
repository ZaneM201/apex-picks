from django.contrib import admin
from django.contrib.auth.models import User

from .models import RacePick, RaceResult, UserSeasonStats


@admin.register(RacePick)
class RacePickAdmin(admin.ModelAdmin):
    list_display = ['user', 'race', 'points_earned', 'picks_locked', 'submitted_at']
    list_filter = ['race', 'picks_locked', 'submitted_at']
    search_fields = ['user__username', 'race__name']
    ordering = ['-race__date', '-points_earned']
    readonly_fields = ['submitted_at', 'updated_at']
    
    def get_fieldsets(self, request, obj=None):
        """Show/hide sprint picks based on race type"""
        return [
            ('Picks Information', {
                'fields': ('user', 'race', 'points_earned', 'picks_locked')
            })
            ('Race Predictions', {
                'fields': (
                    'first_place', 'second_place', 'third_place',
                    'pole_position', 'fastest_lap', 'driver_of_day'
                )
            })
            ('Sprint Predictions', {
                'fields': ('sprint_first', 'sprint_second', 'sprint_third'),
                'classes': ('collapse',),
                'description': 'Only fill these for sprint weekends.'
            }),
            ('Timestamps', {
                'fields': ('submitted_at', 'updated_at'),
                'classes': ('collapse',),
            })    
        ]
    
    actions = ['lock_picks', 'unlock_picks']
    
    def lock_picks(self, request, queryset):
        """Lock selected picks so they cannot be edited"""
        updated = queryset.update(picks_locked=True)
        self.message_user(request, f'{updated} pick(s) successfully locked.')

    lock_picks.short_description = "Lock selected picks"
    
    def unlock_picks(self, request, queryset):
        """Unlock selected picks"""
        updated = queryset.update(picks_locked=False)
        self.message_user(request, f'{updated} pick(s) successfully unlocked.')

    unlock_picks.short_description = "Unlock selected picks"


@admin.register(RaceResult)
class RaceResultAdmin(admin.ModelAdmin):
    list_display = [
        'race', 'first_place', 'second_place', 'third_place', 
        'results_finalized', 'has_driver_of_day', 'dnf_count'
        ]
    list_filter = ['results_finalized', 'race__date', 'race__sprint_race']
    search_fields = ['race__name']
    ordering = ['-race__date']
    
    fieldsets = (
        ('Race & Status', {
            'fields': ('race', 'results_finalized'),
            'description': '⚠️ <strong>IMPORTANT:</strong> Only check "Results finalized" after reviewing ALL data below. '
                          'This will automatically calculate points for all users and lock the results permanently.'
        }),
        ('Race Results - Auto-Populated from API', {
            'fields': ('first_place', 'second_place', 'third_place', 
                      'pole_position', 'fastest_lap'),
            'description': '✅ These fields are auto-populated by running: <code>python manage.py fetch_race_results --race-id X</code><br>'
                          '🔍 <strong>Review carefully!</strong> API data may be incorrect. You can edit any field manually.'
        }),
        ('Manual Entry Required ⚠️', {
            'fields': ('driver_of_day', 'dnf_drivers'),
            'description': '⚠️ <strong>You MUST enter these manually:</strong><br>'
                          '• <strong>Driver of the Day:</strong> Check F1.com or the official F1 app for the fan vote winner<br>'
                          '• <strong>DNF Drivers:</strong> Select all drivers who did not finish the race (retired, disqualified, etc.)'
        }),
        ('Sprint Results - Manual or API', {
            'fields': ('sprint_first', 'sprint_second', 'sprint_third'),
            'classes': ('collapse',),
            'description': 'For sprint race weekends only. May need manual entry depending on API availability.'
        }),
    )
    
    filter_horizontal = ['dnf_drivers']

    def has_driver_of_day(self, obj):
        """Check if Driver of the Day has been set"""
        return obj.driver_of_day is not None
    has_driver_of_day.boolean = True
    has_driver_of_day.short_description = "Driver of the Day Set"

    def dnf_count(self, obj):
        """Show number of DNF drivers"""
        return obj.dnf_drivers.count()
    dnf_count.short_description = "DNFs"

    def save_model(self, request, obj, form, change):
        """Auto calculate points when results are finalized"""
        was_finalized = False

        # Check if this is being finalized now
        if change and obj.results_finalized:
            try:
                old_obj = RaceResult.objects.get(pk=obj.pk)
                if not old_obj.results_finalized:
                    was_finalized = True
            except RaceResult.DoesNotExist:
                pass
        elif not change and obj.results_finalized:
            was_finalized = True

        super().save_model(request, obj, form, change)

        if was_finalized:
            # Vaildate that required fields are filled
            if not obj.driver_of_day:
                self.message_user(request, 'Warning: Driver of the Day is not set. Points calculation may be incorrect.', level='warning')

        # Lock all picks for this race
        picks_locked = RacePick.objects.filter(race=obj.race).update(picks_locked=True)

        # Calculate points for all picks for this race
        picks = RacePick.objects.filter(race=obj.race)
        for pick in picks:
            pick.points_earned = obj.calculate_points_for_pick(pick)
            pick.save()

        # Update user season stats
        self.update_season_stats(obj.race)

        self.message_user(
            request,
            f'✅ SUCCESS! Results finalized for {obj.race.name}:<br>'
                f'• {picks_locked} pick(s) locked<br>'
                f'• Points calculated for {picks.count()} user(s)<br>'
                f'• Season leaderboard updated',
                level='SUCCESS'
        )

    def update_season_stats(self, race):
        """Update overall season stats for all users"""
        for user in User.objects.all():
            stats, created = UserSeasonStats.objects.get_or_create(user=user)

            # Recalculate total points
            user_picks = RacePick.objects.filter(user=user)
            stats.total_points = sum(pick.points_earned for pick in user_picks)
            stats.races_participated = user_picks.count()

            # Count correct poles 
            correct_poles = 0
            for pick in user_picks:
                try:
                    if pick.race.result.pole_position == pick.pole_position:
                        correct_poles += 1  
                except RaceResult.DoesNotExist:
                    continue
            stats.correct_poles = correct_poles

            # Count correct wins
            correct_wins = 0
            for pick in user_picks:
                try:
                    if pick.race.result.first_place == pick.first_place:
                        correct_wins += 1   
                except RaceResult.DoesNotExist:
                    continue    
            stats.correct_wins = correct_wins

            stats.save()


@admin.register(UserSeasonStats)
class UserSeasonStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'races_participated', 'correct_wins', 'correct_poles']
    ordering = ['-total_points', '-correct_wins', '-correct_poles']
    search_fields = ['user__username']
    readonly_fields = ['total_points', 'races_participated', 'correct_wins', 'correct_poles']

    def has_add_permission(self, request):
        """Stats are auto-generated; prevent manual addition"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of stats"""
        return False