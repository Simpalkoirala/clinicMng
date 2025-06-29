from django.contrib import admin
from django.urls import path, include
from doctor.views import * 

app_name = 'doctor'


urlpatterns = [
    
    path('d/view-patients/', ViewPatients, name='ViewPatients_m'),
    path('d/view-doctors/', ViewPatients, name='ViewDoctors_m'),





    path('', doctorDashboard, name='dashboard'),
    path('dashboard/', doctorDashboard, name='doctor_dashboard'),



    path('session-mng/', SessionMng, name='SessionMng'),
    path('availability/<uuid:app_uuid>/', get_doctor_availability_json, name='doctor-availability-json'),


    path('edit-schedules/', d_edit_schedules, name='d_edit_schedules'),
    path('get-dateTime-slots/', get_dateTime_slots, name='get_dateTime_slots_default'),
    path('get-dateTime-slots/<str:start_date>/', get_dateTime_slots, name='get_dateTime_slots'),
    path('submit-dateTime-slots/', submit_dateTime_slots, name='submit_dateTime_slots'),


    path('view-patients/', ViewPatients, name='ViewPatients_d'),
    # path('view-patients-records/<str:patient_id>/', ViewPatientsRecords, name='ViewPatientsRecords'),
 
    path('actions-appointment/', Action_Appointment, name='Action_Appointment_from_Doc'),


    path('message/', message, name='message'),

    # Video Call URLs
    path('view-v-call/', view_v_call, name='view_v_call'), # view calls 
    path('send-req-calls/<uuid:convo_uuid>/', send_req_calls, name='send_req_calls'),
    path('waiting-room/<uuid:calls_uuid>/', waiting_room, name='waiting_room'),
    path('join-v-call/<uuid:calls_uuid>/', join_v_call, name='join_v_call'),


    path('profile/', d_profile, name='profile'),
]
