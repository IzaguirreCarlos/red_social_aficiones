
from django.urls import path
from .views import create_post, follow_user, unfollow_user
from .views import feed

app_name = 'posts'

urlpatterns = [
    path('create/', create_post, name='create_post'),
    path('follow/<int:user_id>/', follow_user, name='follow'),
    path('unfollow/<int:user_id>/', unfollow_user, name='unfollow'),
    path('', feed, name='feed'),
]
