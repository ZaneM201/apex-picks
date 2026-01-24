from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from drivers.models import Driver
from schedule.models import Schedule


class RacePick(models.Model):  # Changed from RacePicks to RacePick (singular)
    """User's picks for a specific race"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='race_picks')
    race = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='picks')

    # Race predictions
    first_place = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='first_place_picks')
    second_place = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='second_place_picks')
    third_place = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='third_place_picks')
    pole_position = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='pole_picks')  # Changed from pole_position_picks
    fastest_lap = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='fastest_lap_picks')
    driver_of_day = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='dotd_picks')  # Changed from driver_of_the_day

    # Sprint predictions (if applicable)
    sprint_first = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='sprint_first_picks', null=True, blank=True)
    sprint_second = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='sprint_second_picks', null=True, blank=True)
    sprint_third = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='sprint_third_picks', null=True, blank=True)

    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    points_earned = models.IntegerField(default=0)
    picks_locked = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'race']
        ordering = ['-race__date']

    def __str__(self):
        return f"{self.user.username} - {self.race.name}"

    def can_edit(self):
        """Check if user can still edit their picks"""
        return not self.picks_locked and timezone.now() < self.race.date

    def clean(self):
        """Validate that picks are different drivers"""
        from django.core.exceptions import ValidationError

        podium_picks = [self.first_place, self.second_place, self.third_place]
        if len(set(podium_picks)) != 3:
            raise ValidationError("Podium positions must be different drivers")

        if self.race.sprint_race:
            sprint_picks = [self.sprint_first, self.sprint_second, self.sprint_third]
            if None not in sprint_picks and len(set(sprint_picks)) != 3:
                raise ValidationError("Sprint podium positions must be different drivers")
        else:
            if self.sprint_first or self.sprint_second or self.sprint_third:
                raise ValidationError("There is no Sprint Race this weekend")


class RaceResult(models.Model):
    """Actual results of a race for scoring"""
    race = models.OneToOneField(Schedule, on_delete=models.CASCADE, related_name='result')

    # Race results
    first_place = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='first_place_results')
    second_place = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='second_place_results')
    third_place = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='third_place_results')
    pole_position = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='pole_results')  # Changed from pole_position_results
    fastest_lap = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='fastest_lap_results')
    driver_of_day = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='dotd_results')  # Changed from driver_of_the_day

    # DNFs for penalty calculation
    dnf_drivers = models.ManyToManyField(Driver, related_name='dnf_races', blank=True)  # Changed related_name

    # Sprint results (if applicable)
    sprint_first = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='sprint_first_results', null=True, blank=True)
    sprint_second = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='sprint_second_results', null=True, blank=True)
    sprint_third = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='sprint_third_results', null=True, blank=True)

    results_finalized = models.BooleanField(default=False)

    def __str__(self):
        return f"Results: {self.race.name}"

    def calculate_points_for_pick(self, race_pick):  # Fixed method name and parameter
        """Calculate points for a user's pick based on actual results"""
        points = 0

        # Race weekend points
        if race_pick.first_place == self.first_place:
            points += 25
        elif race_pick.first_place in self.dnf_drivers.all():
            points -= 25  # DNF penalty

        if race_pick.second_place == self.second_place:
            points += 18
        elif race_pick.second_place in self.dnf_drivers.all():
            points -= 18

        if race_pick.third_place == self.third_place:
            points += 15
        elif race_pick.third_place in self.dnf_drivers.all():
            points -= 15

        if race_pick.pole_position == self.pole_position:
            points += 10

        if race_pick.fastest_lap == self.fastest_lap:
            points += 5

        if race_pick.driver_of_day == self.driver_of_day:
            points += 20

        # Sprint points
        if self.race.sprint_race:
            if race_pick.sprint_first == self.sprint_first:
                points += 8
            elif race_pick.sprint_first in self.dnf_drivers.all():
                points -= 8

            if race_pick.sprint_second == self.sprint_second:
                points += 7
            elif race_pick.sprint_second in self.dnf_drivers.all():
                points -= 7

            if race_pick.sprint_third == self.sprint_third:
                points += 6
            elif race_pick.sprint_third in self.dnf_drivers.all():
                points -= 6

        return points


class UserSeasonStats(models.Model):
    """Track user's overall season statistics"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='season_stats')
    total_points = models.IntegerField(default=0)
    correct_poles = models.IntegerField(default=0)
    correct_wins = models.IntegerField(default=0)
    races_participated = models.IntegerField(default=0)

    class Meta:
        ordering = ['-total_points', '-correct_wins', '-correct_poles', '-races_participated']
        verbose_name_plural = "User Season Stats"

    def __str__(self):
        return f"{self.user.username} - {self.total_points} pts"