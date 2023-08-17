from django.db.models.signals import Signal
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail

user_created = Signal()


@receiver(user_created, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        send_mail(
            "Welcome to our site",
            "Thank you for joining us!",
            "manhnguyen1104010@gmail.com",
            [instance.email],
            fail_silently=False,
        )
