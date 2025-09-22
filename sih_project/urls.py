"""
URL configuration for sih_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('students/', include('students.urls')),
    path('teachers/', include('teachers.urls')),
    path('admins/', include('admins.urls')),
    path("ai/", include("ai_suggestions.urls", namespace="ai_suggestions")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

