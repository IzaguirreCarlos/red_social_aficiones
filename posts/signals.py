"""Señales que crean Notifications automáticamente al ocurrir eventos sociales.

Reglas:
- Like:    notifica al author del post (si no es uno mismo).
- Comment: notifica al author del post (si no es uno mismo).
- Follow:  notifica al usuario seguido.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Like, Comment, Follow, Notification


@receiver(post_save, sender=Like)
def notify_on_like(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.user_id == instance.post.author_id:
        return
    Notification.objects.create(
        recipient=instance.post.author,
        sender=instance.user,
        notification_type=Notification.LIKE,
        post=instance.post,
    )


@receiver(post_delete, sender=Like)
def cleanup_on_unlike(sender, instance, **kwargs):
    """Borra la notificación de like asociada cuando el usuario quita el like."""
    Notification.objects.filter(
        recipient=instance.post.author,
        sender=instance.user,
        notification_type=Notification.LIKE,
        post=instance.post,
    ).delete()


@receiver(post_save, sender=Comment)
def notify_on_comment(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.author_id == instance.post.author_id:
        return
    Notification.objects.create(
        recipient=instance.post.author,
        sender=instance.author,
        notification_type=Notification.COMMENT,
        post=instance.post,
    )


@receiver(post_save, sender=Follow)
def notify_on_follow(sender, instance, created, **kwargs):
    if not created:
        return
    Notification.objects.create(
        recipient=instance.following,
        sender=instance.follower,
        notification_type=Notification.FOLLOW,
    )


@receiver(post_delete, sender=Follow)
def cleanup_on_unfollow(sender, instance, **kwargs):
    Notification.objects.filter(
        recipient=instance.following,
        sender=instance.follower,
        notification_type=Notification.FOLLOW,
    ).delete()
