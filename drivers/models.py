from django.db import models

# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=100)
    base = models.CharField(max_length=100)
    principal = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='media/team_logos/', blank=True)


    def __str__(self):
        return self.name

class Driver(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    number = models.IntegerField(unique=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    country = models.CharField(max_length=100)
    flag = models.ImageField(upload_to='media/flags/', blank=True)
    image = models.ImageField(upload_to='media/driver_images/', blank=True)
    pole_positions = models.IntegerField(default=0)
    race_wins = models.IntegerField(default=0)
    podiums = models.IntegerField(default=0)
    world_championships = models.IntegerField(default=0)


    def __str__(self):
        return self.first_name + " " + self.last_name