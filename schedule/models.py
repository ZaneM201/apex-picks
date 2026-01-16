from django.db import models

# Create your models here.
class Schedule(models.Model):
    name = models.CharField(max_length=100)
    track_image = models.ImageField(upload_to='media/track_images/')
    date = models.DateField()
    description = models.TextField()

    def __str__(self):
        return self.name