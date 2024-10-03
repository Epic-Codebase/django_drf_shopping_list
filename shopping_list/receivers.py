from django.db.models.signals import post_save
from django.dispatch import receiver

from shopping_list.models import ShoppingItem, ShoppingList


@receiver(post_save, sender=ShoppingItem)
def interaction_with_shopping_list(sender, instance, **kwargs):
    ShoppingList.objects.get(id=instance.shopping_list.id).save(
        update_fields=["last_interaction"]
    )
