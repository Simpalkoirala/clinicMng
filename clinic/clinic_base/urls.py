
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from patient.views import view_v_call, send_req_calls, waiting_room, join_v_call

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
 
    path('account/', include('account.urls')),


    path('view-v-call/', view_v_call, name='view_v_call'), # view calls 
    path('send-req-calls/<uuid:convo_uuid>/', send_req_calls, name='send_req_calls'),
    path('waiting-room/<uuid:calls_uuid>/', waiting_room, name='waiting_room'),
    path('join-v-call/<uuid:calls_uuid>/', join_v_call, name='join_v_call'),

    path('p/', include('patient.urls')),
    path('d/', include('doctor.urls')),
    # path('m/', include('management.urls')),

    ]


# Temporary media serving (not suitable for production)
if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)