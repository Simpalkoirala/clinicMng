from django.contrib import admin
from django.urls import path, include
from .views import * 


urlpatterns = [
    path('', home_page, name='home'),
    path('2/', home_page2, name='home2'),


    path('terms/', terms, name='terms'),





    # path('patient/old', patientDashboardOld, name='patientDashboardold'),


    path('management/', management, name='management_dashboard'),
    path('m/view-patients/', ViewPatients, name='ViewPatients_m'),
    path('m/view-doctors/', ViewPatients, name='ViewDoctors_m'),


]