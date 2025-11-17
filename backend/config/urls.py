"""
URL configuration for game topup project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView  # Disabled for quick start

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API Documentation - Disabled for quick start
    # path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # API endpoints
    path('api/users/', include('apps.users.urls')),
    path('api/games/', include('apps.games.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/wallets/', include('apps.wallets.urls')),

    # Frontend views
    path('', include('apps.core.urls')),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Serve static files from STATICFILES_DIRS
    from django.contrib.staticfiles.views import serve as static_serve
    from django.views.static import serve
    import os

    # Serve from frontend/static directory
    for static_dir in settings.STATICFILES_DIRS:
        if os.path.exists(static_dir):
            urlpatterns += static(settings.STATIC_URL, document_root=static_dir)

# Admin site customization
admin.site.site_header = "Game TopUp Admin"
admin.site.site_title = "Game TopUp Admin Portal"
admin.site.index_title = "Welcome to Game TopUp Administration"
