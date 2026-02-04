from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile')
    picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone_number = models.TextField(max_length=20)
    zip_code = models.TextField(max_length=10)

    def __str__(self):
        return f"profile for: {self.user}"