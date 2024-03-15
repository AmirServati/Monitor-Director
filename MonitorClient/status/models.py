from django.db import models

# Create your models here.
class Monitor(models.Model):
    source = models.CharField(max_length = 10)