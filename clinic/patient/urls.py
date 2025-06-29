from django.contrib import admin
from django.urls import path, include
from patient.views import * 

app_name = 'patient'


urlpatterns = [
    path('', patientDashboard, name='dashboard'),
    path('dashboard/', patientDashboard, name='patientDashboard'),
    path('view-appointment/', viewAppointment, name='viewAppointment'),
    path('appointment/<uuid:apot_id>/<str:status>/', appoinemtCancle_Edit, name='appoinemtCancle_Edit'),

    path('exp-app-excel/', export_appointments_excel, name='export_appointments_excel'),

    path('book-appointment/', BookAppointment, name='bookAppointment'),
    path('document/', ViewDocument, name='viewDocument'),
    path('delete-document/<int:doc_id>/', delete_document, name='deleteDocument'),





    path('lab-report/', labReport, name='labReport'),
    path('lab-report/<uuid:uuid>/download/', lab_report_pdf, name='lab_report_pdf'),



    path('prescriptions/', prescriptions, name='prescriptions'),
    path('profile/', p_profile, name='profile'),
    path('activities/', p_activities, name='activities'),

    # path('message/<int:conversation_id>/', conversation_view, name='conversation_view'),

    path('message/', message, name='message'),
    path('get-msg/<int:conversation_id>/', get_msg_list, name='conversation_view'),
    path('send-msg/', post_msg, name='send_msg'),

    # Video Call URLs
    path('view-v-call/', view_v_call, name='view_v_call'), # view calls 
    path('send-req-calls/<uuid:convo_uuid>/', send_req_calls, name='send_req_calls'),
    path('waiting-room/<uuid:calls_uuid>/', waiting_room, name='waiting_room'),
    path('join-v-call/<uuid:calls_uuid>/', join_v_call, name='join_v_call'),


    path('req-conv/', req_conv, name='req_conv'),
    

]