from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_updated
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


@receiver(social_account_updated)
def update_profile_photo_from_google(sender, request, sociallogin, **kwargs):
    """
    When a user logs in with Google, extract their profile photo URL
    and save it to their UserProfile.
    """
    if sociallogin.account.provider == 'google':
        user = sociallogin.user
        extra_data = sociallogin.account.extra_data
        
        # Google provides the profile photo in the 'picture' field
        photo_url = extra_data.get('picture', '')
        
        if photo_url:
            # Get or create the UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.profile_photo_url = photo_url
            profile.save(update_fields=['profile_photo_url'])


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile when a new user is created.
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=SocialAccount)
def update_existing_user_photo(sender, instance, created, **kwargs):
    """
    Update profile photo for existing users when their social account is updated.
    """
    if instance.provider == 'google':
        photo_url = instance.extra_data.get('picture', '')
        if photo_url:
            profile, _ = UserProfile.objects.get_or_create(user=instance.user)
            if profile.profile_photo_url != photo_url:
                profile.profile_photo_url = photo_url
                profile.save(update_fields=['profile_photo_url'])