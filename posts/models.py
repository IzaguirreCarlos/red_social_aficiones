from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author.username} - {self.created_at}'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author.username}'


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f'{self.user.username} likes {self.post.id}'


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'


class Notification(models.Model):
    """Notificaciones que un usuario recibe.
    type: like / comment / follow
    """
    LIKE    = 'like'
    COMMENT = 'comment'
    FOLLOW  = 'follow'
    TYPE_CHOICES = [
        (LIKE,    'Like'),
        (COMMENT, 'Comment'),
        (FOLLOW,  'Follow'),
    ]

    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications'
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_notifications'
    )
    notification_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, null=True, blank=True,
        related_name='notifications'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f'{self.notification_type} {self.sender.username} → {self.recipient.username}'

    @property
    def verb(self):
        return {
            self.LIKE:    'le dio like a tu publicación',
            self.COMMENT: 'comentó tu publicación',
            self.FOLLOW:  'comenzó a seguirte',
        }[self.notification_type]
