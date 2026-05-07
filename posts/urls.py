from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    # Feed (muro)
    path('', views.feed, name='feed'),
    path('feed/load/', views.feed_load_more, name='feed_load_more'),

    # Posts
    path('create/', views.create_post, name='create_post'),

    # Likes / comentarios (AJAX)
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('comment/<int:post_id>/', views.create_comment, name='create_comment'),

    # Follow / Unfollow + explore
    path('explore/', views.explore_users, name='explore'),
    path('follow/<int:user_id>/', views.follow_user, name='follow'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow'),
]
