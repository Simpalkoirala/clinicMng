from django.contrib import admin
from django.urls import path, include
from .views import * 


urlpatterns = [
    path('', home_page, name='home'),
    path('2/', home_page2, name='home2'),


    path('terms/', terms, name='terms'),


    path('view-patients-records/<str:patient_id>/', ViewPatientsRecords, name='ViewPatientsRecords'),


    # path('patient/old', patientDashboardOld, name='patientDashboardold'),
]