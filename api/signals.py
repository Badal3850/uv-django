# To automatically create/update UserProfile when User is created/updated:
    # This is commonly done using signals. Create a signals.py file in your app:
    #
    # # your_app_name/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User # Or your custom user model
from .models import UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist: # Should not happen if created above, but good practice
        UserProfile.objects.create(user=instance)