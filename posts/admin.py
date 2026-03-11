from django.contrib import admin
from .models import Post, Comment, Like, Follow

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from .models import Post, Comment, Like, Follow


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'short_content',
        'image_preview',
        'likes_count',
        'comments_count',
        'created_at'
    )

    search_fields = ('content', 'author__username')
    list_filter = ('created_at',)

    # Muestra los primeros 50 caracteres del post
    def short_content(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    short_content.short_description = "Content"

    # Cuenta los likes
    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = "Likes"

    # Cuenta los comentarios
    def comments_count(self, obj):
        return obj.comments.count()
    comments_count.short_description = "Comments"

    # Muestra una miniatura de la imagen
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "-"
    image_preview.short_description = "Image"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'content', 'created_at')
    search_fields = ('content', 'author__username')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
