"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


urlpatterns = [
    # Landing pública (con video de fondo). Si el usuario está logueado,
    # la propia vista del feed sigue siendo accesible en /feed/
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),

    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('posts/', include('posts.urls')),  # incluye /posts/feed/, etc.
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL or '/media/',
                          document_root=getattr(settings, 'MEDIA_ROOT', ''))
