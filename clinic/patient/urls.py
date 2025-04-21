from django.contrib import admin
from django.urls import path, include
from patient.views import * 

app_name = 'patient'


urlpatterns = [

    
    path('', patientDashboard, name='patient_dashboard'),
    path('dashboard/', patientDashboard, name='patient_dashboard2'),
    path('view-appoinment/', viewAppoinment, name='viewAppoinment'),
    path('book-appoinment/', BookAppoinment, name='BookAppoinment'),
    path('document/', ViewDocument, name='ViewDocument'),
    path('delete-document/<int:doc_id>/', delete_document, name='deleteDocument'),

    path('join-v-call/', join_v_call, name='join_v_call'),
    path('lab-report/', labReport, name='labReport'),
    path('prescriptions/', prescriptions, name='prescriptions'),
    path('message/', message, name='p-message'),
    path('profile/', p_profile, name='profile'),




    

]