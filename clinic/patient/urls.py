from django.contrib import admin
from django.urls import path, include
from patient.views import * 

app_name = 'patient'


urlpatterns = [

    
    path('', patientDashboard, name='patientDashboard'),
    path('dashboard/', patientDashboard, name='patient_dashboard2'),
    path('view-appointment/', viewAppointment, name='viewAppointment'),
    path('appointment/<uuid:apot_id>/<str:status>/', appoinemtCancle_Edit, name='appoinemtCancle_Edit'),

    path('exp-app-excel/', export_appointments_excel, name='export_appointments_excel'),

    path('book-appointment/', BookAppointment, name='bookAppointment'),
    path('document/', ViewDocument, name='viewDocument'),
    path('delete-document/<int:doc_id>/', delete_document, name='deleteDocument'),

    path('join-v-call/', join_v_call, name='join_v_call'),
    path('lab-report/', labReport, name='labReport'),
    path('lab-report/<uuid:uuid>/download/', lab_report_pdf, name='lab_report_pdf'),



    path('prescriptions/', prescriptions, name='prescriptions'),
    path('message/', message, name='message'),
    path('profile/', p_profile, name='profile'),
    path('activities/', p_activities, name='activities'),




    

]