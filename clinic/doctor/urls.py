from django.contrib import admin
from django.urls import path, include
from doctor.views import * 

app_name = 'doctor'


urlpatterns = [
    path('', doctorDashboard, name='doctor_dashboard'),
    path('dashboard/', doctorDashboard, name='doctor_dashboard'),
    path('edit-schedules/', d_edit_schedules, name='d_edit_schedules'),
    path('view-patients/', ViewPatients, name='ViewPatients_d'),
    path('online-session/', OnlineSession, name='OnlineSession'),
    path('d/view-patients/', ViewPatients, name='ViewPatients_m'),
    path('d/view-doctors/', ViewPatients, name='ViewDoctors_m'),
    



    path('setting/', dSetting, name='dSetting'),
    path('profile/', d_profile, name='profile'),
]
