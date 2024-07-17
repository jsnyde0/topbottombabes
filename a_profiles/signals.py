from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_update_profile(sender, instance, created, **kwargs):
    user = instance
    if created:
        Profile.objects.create(user=user, email=user.email)

    # if the user email is updated, update the profile email
    elif user.email != Profile.objects.get(user=user).email:
        Profile.objects.update(email=user.email)

# signal that updates the user email when the profile email is updated
@receiver(post_save, sender=Profile)
def update_user_email(sender, instance, created, **kwargs):
    profile = instance  
    if not created and profile.email != User.objects.get(id=profile.user.id).email:
        User.objects.update(email=profile.email)

# signal that deletes the profile when the user is deleted
@receiver(post_delete, sender=User)
def delete_profile(sender, instance, **kwargs):
    Profile.objects.get(user=instance).delete()

