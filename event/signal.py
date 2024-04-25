from django.db.models.signals import post_init
from django.dispatch import receiver
from django.utils import timezone
from event.models import Event

@receiver(post_init, sender=Event)
def update_market_category_on_init(sender, instance, **kwargs):
    setattr(instance, '_original_start_date', instance.start_date)
    setattr(instance, '_original_end_date', instance.end_date)
    setattr(instance, '_original_market', instance.market)

@receiver(post_init, sender=Event)
def check_market_category(sender, instance, **kwargs):
    now = timezone.now().date()

    if instance.start_date != getattr(instance, '_original_start_date', None) or \
       instance.end_date != getattr(instance, '_original_end_date', None):

        if instance.start_date > now:
            instance.market = "upcoming"
        elif instance.start_date <= now <= instance.end_date:
            instance.market = "active"
        else:
            instance.market = "recent"
        
        setattr(instance, '_original_start_date', instance.start_date)
        setattr(instance, '_original_end_date', instance.end_date)
        setattr(instance, '_original_market', instance.market)
