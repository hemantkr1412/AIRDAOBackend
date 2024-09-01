from django.db import models
import random
from django.core.exceptions import ValidationError
from django.utils import timezone
from user.models import Account
from decimal import Decimal
from event.contract_call import create_event, update_event, close_event


def avatarupload(instance, filename):
    file_extension = filename.split(".")[-1]
    new_file_name = str(random.randrange(1000, 1000000)) + "." + file_extension
    return "/".join(["avatar", new_file_name])


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class PossibleResult(models.Model):
    event = models.ForeignKey(
        "Event", related_name="possible_results", on_delete=models.CASCADE
    )
    result = models.CharField(max_length=255)

    def __str__(self):
        return self.result

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
    final_result = models.ForeignKey(
        PossibleResult,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events",
    )
    platform_share = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    event_id = models.IntegerField(blank=True, null=True)
    create_event_tx_receipt = models.CharField(max_length=255, blank=True, null=True)
    update_event_tx_receipt = models.CharField(max_length=255, blank=True, null=True)
    close_event_tx_receipt = models.CharField(max_length=255, null=True, blank=True)

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

    def calculate_winner_distribution(self):
        # Calculate the total amount to distribute
        total_staked = self.token_volume
        self.platform_share = total_staked * Decimal("0.10")
        distribution_amount = total_staked - self.platform_share
        print("calling this")

        # Get all winning votes
        winning_votes = Vote.objects.filter(possible_result=self.final_result)

        # Calculate the total tokens staked on the winning result
        total_winning_staked = (
            winning_votes.aggregate(total=models.Sum("token_staked"))["total"] or 0
        )
        if total_winning_staked == 0:
            return 0, self.platform_share  # Or handle as necessary

        # Distribute the tokens among the winners based on their contribution
        for vote in winning_votes:
            contribution_percentage = vote.token_staked / total_winning_staked
            reward_amount = distribution_amount * contribution_percentage
            vote.amount_rewarded = reward_amount
            vote.save(update_fields=["amount_rewarded"])

        return distribution_amount, self.platform_share

    # def resolve_event(self, final_result):
    #     self.final_result = final_result
    #     self.save(update_fields=["final_result"])
    #     # Calculate and distribute rewards
    #     distribution_amount, platform_share = self.calculate_winner_distribution()

    #     return distribution_amount, platform_share


class Vote(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    possible_result = models.ForeignKey(PossibleResult, on_delete=models.CASCADE)
    token_staked = models.PositiveIntegerField(null=True, blank=True)
    tx_hash = models.CharField(max_length=512, null=True, blank=True)
    amount_rewarded = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Vote by {self.account} for {self.possible_result.result}"
