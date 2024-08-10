from django.db import models


class Account(models.Model):
    account = models.CharField(max_length=255, unique=True)
