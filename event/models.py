from django.db import models
import random
from django.core.exceptions import ValidationError
from django.utils import timezone
from user.models import User


def avatarupload(instance, filename):
    file_extension = filename.split(".")[-1]
    new_file_name = str(random.randrange(1000, 1000000)) + "." + file_extension
    return "/".join(["avatar", new_file_name])


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="events"
    )
    event_name = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to=avatarupload, null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    resolution_date = models.DateTimeField()
    token_volume = models.PositiveIntegerField(default=0, null=True, blank=True)
    min_token_stake = models.PositiveIntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.event_name

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError("End date should be after start date")
        if self.resolution_date <= self.end_date:
            raise ValidationError("Resolution date should be after end date")

    @property
    def market(self):
        now = timezone.now()

        if self.start_date is None:
            return "start date not set"
        elif self.start_date > now:
            return "upcoming"
        elif self.start_date <= now <= self.end_date:
            return "active"
        else:
            return "recent"


class PossibleResult(models.Model):
    event = models.ForeignKey(
        "Event", related_name="possible_results", on_delete=models.CASCADE
    )
    result = models.CharField(max_length=255)


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    possible_result = models.ForeignKey(PossibleResult, on_delete=models.CASCADE)
    token_staked = models.PositiveIntegerField(null=True, blank=True)
    tx_hash = models.CharField(max_length=512, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "user",
            "possible_result",
        )

    def __str__(self):
        return f"Vote by {self.user} for {self.possible_result.result}"
