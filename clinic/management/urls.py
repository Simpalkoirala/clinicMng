from django.contrib import admin
from django.urls import path, include
from management.views import *
 
app_name = 'management'


urlpatterns = [
    path('management/', management_dashboard, name='management_dashboard'),
    path('', management_dashboard, name='dashboard'),
    path('view-appointments/', ViewAppointmnets, name='viewAppointment'),

    
    path('view-patients/', ViewPatients, name='ViewPatients'),
    path('create-patients/', create_patient, name='create_patient'),
    path('update-profile/<str:username>/', update_profile, name='update_profile'),
    path('update-medical-info/<str:username>/', update_medical_info, name='update_medical_info'),


    path('view-doctors/', ViewDoctors, name='ViewDoctors'),
    path('edit-doc/', EditDoctorInfo, name='edit_doctor_info'),
    path('create-doctors/', create_doctor, name='api_create_doctor'),


    path('medicine-mng/', medicineMng, name='medicineMng'),
    path('medicine-mng/<uuid:medicine_uuid>/delete/', delete_medicine, name='deleteMedicine'),

    path('prescriptions-mng/', precpMng, name='prescriptionsMng'),
    path('prescriptions/add/', add_prescription, name='add_prescription'),
    path('prescriptions/delete/<uuid:prescription_uuid>/', delete_prescription, name='add_prescription'),
    path('edit-pres-mng/<uuid:prescription_uuid>/', edit_prescription, name='EditPrescriptionsMng'),

    path('labreport-mng/', labRpMng, name='labreportMng'),
    path('edit-labreport-mng/<uuid:labReport_uuid>/', update_lab_report, name='editlabreportMng'),
    path('labreport-mng/create/', create_lab_report, name='create_lab_report'),
    path('labreport-mng/delete/<uuid:labReport_uuid>/', delete_lab_report, name='delete_lab_report'),


    path('message/', message, name='message'),
]