from django.shortcuts import render, redirect
from .models import Post
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Follow

from django.db.models import Q



# Create your views here.

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:feed')
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})





@login_required
def follow_user(request, user_id):
    target = User.objects.get(id=user_id)
    Follow.objects.get_or_create(follower=request.user, following=target)
    return JsonResponse({'status': 'ok'})

@login_required
def unfollow_user(request, user_id):
    target = User.objects.get(id=user_id)
    Follow.objects.filter(follower=request.user, following=target).delete()
    return JsonResponse({'status': 'ok'})





@login_required
def feed(request):
    # Lista de usuarios que sigo
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    # Posts de usuarios seguidos
    posts = Post.objects.filter(author__in=following_ids).order_by('-created_at')
    return render(request, 'posts/feed.html', {'posts': posts})
