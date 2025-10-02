from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomerProfile, FarmerProfile, User, UserProfile


@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    """
    Automatically create profiles when a user is created
    """
    if created:
        # Always create basic user profile
        UserProfile.objects.get_or_create(user=instance)

        # Create role-specific profiles
        if instance.user_type == "customer":
            CustomerProfile.objects.get_or_create(user=instance)
        elif instance.user_type == "farmer":
            # Create farmer profile with minimal required fields
            FarmerProfile.objects.get_or_create(
                user=instance, defaults={"farm_name": f"{instance.username}'s Farm"}
            )


@receiver(post_save, sender=User)
def save_user_profiles(sender, instance, **kwargs):
    """
    Save profiles when user is saved
    """
    if hasattr(instance, "profile"):
        instance.profile.save()

    if instance.user_type == "customer" and hasattr(instance, "customer_profile"):
        instance.customer_profile.save()

    if instance.user_type == "farmer" and hasattr(instance, "farmer_profile"):
        instance.farmer_profile.save()
