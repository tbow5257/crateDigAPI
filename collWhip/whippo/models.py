from django.db import models

# Create your models here.

class Album(models.Model):
    name = models.CharField(max_length=400)
    releaseId = models.CharField(max_length=50)
    style = models.CharField(max_length=50)
    have = models.IntegerField()
    want = models.IntegerField()
    price = models.IntegerField()

    def __str__(self):
        return self.name + ' ' + self.releaseId

class Style(models.Model):
    name = models.CharField(max_length=200)