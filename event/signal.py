from django.db.models.signals import post_init
from django.dispatch import receiver
from django.utils import timezone
from event.models import Event
from django.db.models.signals import post_save
from event.contract_call import create_event, close_event
from django.db import transaction


@receiver(post_init, sender=Event)
def update_market_category_on_init(sender, instance, **kwargs):
    setattr(instance, "_original_start_date", instance.start_date)
    setattr(instance, "_original_end_date", instance.end_date)
    setattr(instance, "_original_market", instance.market)


@receiver(post_init, sender=Event)
def check_market_category(sender, instance, **kwargs):
    now = timezone.now().date()

    if instance.start_date != getattr(
        instance, "_original_start_date", None
    ) or instance.end_date != getattr(instance, "_original_end_date", None):

        if instance.start_date > now:
            instance.market = "upcoming"
        elif instance.start_date <= now <= instance.end_date:
            instance.market = "active"
        else:
            instance.market = "recent"

        setattr(instance, "_original_start_date", instance.start_date)
        setattr(instance, "_original_end_date", instance.end_date)
        setattr(instance, "_original_market", instance.market)


@receiver(post_save, sender=Event)
def trigger_create_event(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: handle_event_creation(instance))


def handle_event_creation(event_instance):
    outcomes = [result.result for result in event_instance.possible_results.all()]
    if outcomes:  # Ensure outcomes are not empty
        result = create_event(event_instance.id, event_instance.event_name, outcomes)
        # tx_hash = result["tx_hash"]
        # event_id = result["event_id"]
        # print("tx_hash", tx_hash)
        # print("event_id", event_id)
        event_instance.create_event_tx_receipt = result
        # event_instance.event_id = event_id
        event_instance.save(update_fields=["create_event_tx_receipt"])


def handle_event_resolution(event_instance):
    if getattr(event_instance, "_processing_final_result", False):
        return  # Prevent recursive triggering

    # Set the flag to prevent recursion
    event_instance._processing_final_result = True

    # Retrieve all possible outcomes for the event
    possible_outcomes = list(event_instance.possible_results.all())
    print("possible", possible_outcomes)

    # Find the final result's index among the possible outcomes
    try:
        final_outcome_index = possible_outcomes.index(event_instance.final_result)
    except ValueError:
        raise ValueError("Final result not found among possible outcomes.")

    print("index", final_outcome_index)
    tx_hash = close_event(event_instance.event_id, final_outcome_index)
    print("Resolution transaction hash:", tx_hash)

    event_instance.close_event_tx_receipt = tx_hash
    event_instance.save(update_fields=["close_event_tx_receipt"])
    event_instance._processing_final_result = False


@receiver(post_save, sender=Event)
def trigger_resolve_event(sender, instance, **kwargs):
    if instance.final_result is not None and instance.id:
        instance.calculate_winner_distribution()
        transaction.on_commit(lambda: handle_event_resolution(instance))

