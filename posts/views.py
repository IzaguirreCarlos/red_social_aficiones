from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.db.models import Q, Count, Exists, OuterRef

from .models import Post, Like, Follow, Comment, Notification
from .forms import PostForm, CommentForm


# ---------- Helpers ----------

POSTS_PER_PAGE = 5


def _annotate_posts(qs, user):
    qs = qs.annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True),
    )
    if user.is_authenticated:
        qs = qs.annotate(
            liked_by_me=Exists(
                Like.objects.filter(post=OuterRef('pk'), user=user)
            )
        )
    return qs


def _feed_queryset(user):
    following_ids = Follow.objects.filter(
        follower=user
    ).values_list('following_id', flat=True)
    qs = Post.objects.filter(
        Q(author__in=following_ids) | Q(author=user)
    ).select_related('author').order_by('-created_at')
    return _annotate_posts(qs, user)


# ---------- Feed ----------

@login_required
def feed(request):
    qs = _feed_queryset(request.user)
    paginator = Paginator(qs, POSTS_PER_PAGE)
    page = paginator.get_page(1)
    return render(request, 'posts/feed.html', {
        'posts': page.object_list,
        'page_obj': page,
        'has_next': page.has_next(),
        'next_page': page.next_page_number() if page.has_next() else None,
        'comment_form': CommentForm(),
    })


@login_required
def feed_load_more(request):
    try:
        page_num = int(request.GET.get('page', 2))
    except (TypeError, ValueError):
        return HttpResponseBadRequest('page inválida')
    qs = _feed_queryset(request.user)
    paginator = Paginator(qs, POSTS_PER_PAGE)
    page = paginator.get_page(page_num)
    html = render_to_string(
        'posts/_post_list.html',
        {'posts': page.object_list, 'comment_form': CommentForm()},
        request=request,
    )
    return JsonResponse({
        'html': html,
        'has_next': page.has_next(),
        'next_page': page.next_page_number() if page.has_next() else None,
    })


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


# ---------- Likes ----------

@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'likes_count': post.likes.count()})


# ---------- Comentarios ----------

@login_required
@require_POST
def create_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
    comment = form.save(commit=False)
    comment.post = post
    comment.author = request.user
    comment.save()
    return JsonResponse({
        'ok': True,
        'comment': {
            'id': comment.id,
            'author': comment.author.username,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%d %b %Y · %H:%M'),
        },
        'comments_count': post.comments.count(),
    })


# ---------- Follow / Unfollow / Explore ----------

@login_required
@require_POST
def follow_user(request, user_id):
    if user_id == request.user.id:
        return JsonResponse({'ok': False, 'error': 'No puedes seguirte a ti mismo'}, status=400)
    target = get_object_or_404(User, id=user_id)
    Follow.objects.get_or_create(follower=request.user, following=target)
    return JsonResponse({
        'ok': True, 'following': True,
        'followers_count': target.followers.count(),
    })


@login_required
@require_POST
def unfollow_user(request, user_id):
    target = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, following=target).delete()
    return JsonResponse({
        'ok': True, 'following': False,
        'followers_count': target.followers.count(),
    })


@login_required
def explore_users(request):
    following_ids = set(
        Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    )
    users = (
        User.objects.exclude(id=request.user.id)
        .annotate(followers_count=Count('followers', distinct=True))
        .order_by('-followers_count', 'username')
    )
    decorated = []
    for u in users:
        u.is_following = u.id in following_ids
        decorated.append(u)
    return render(request, 'posts/explore.html', {'users': decorated})


# ---------- Notificaciones ----------

@login_required
def notifications_list(request):
    """Lista todas las notificaciones del usuario y las marca como leídas."""
    qs = (request.user.notifications
          .select_related('sender', 'post')
          .all()[:50])
    # Marcamos como leídas las nuevas (en una sola query)
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'posts/notifications.html', {'notifications': qs})


@login_required
def notifications_count(request):
    """Polling AJAX: cuántas notificaciones sin leer tiene el usuario."""
    n = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'unread': n})
