
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),

    path('account/', include('account.urls')),

    path('p/', include('patient.urls')),
    path('d/', include('doctor.urls')),
    # path('m/', include('management.urls')),

    ]


# Temporary media serving (not suitable for production)
if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)