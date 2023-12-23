from django.db import models

# Create your models here.

class User(models.Model):
    id = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=20)
    email = models.CharField(max_length=30)
    phone = models.IntegerField()
