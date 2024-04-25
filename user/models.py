from django.db import models


class User(models.Model):
    account = models.CharField(max_length=255)
