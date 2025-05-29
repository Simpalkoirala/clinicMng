from django.contrib import admin
from django.urls import path, include
from doctor.views import * 

app_name = 'doctor'


urlpatterns = [
    
    path('d/view-patients/', ViewPatients, name='ViewPatients_m'),
    path('d/view-doctors/', ViewPatients, name='ViewDoctors_m'),





    path('', doctorDashboard, name='doctor_dashboard'),
    path('dashboard/', doctorDashboard, name='doctor_dashboard'),



    path('session-mng/', SessionMng, name='SessionMng'),
    path('availability/<uuid:app_uuid>/', get_doctor_availability_json, name='doctor-availability-json'),


    path('edit-schedules/', d_edit_schedules, name='d_edit_schedules'),
    path('get-dateTime-slots/', get_dateTime_slots, name='get_dateTime_slots_default'),
    path('get-dateTime-slots/<str:start_date>/', get_dateTime_slots, name='get_dateTime_slots'),
    path('submit-dateTime-slots/', submit_dateTime_slots, name='submit_dateTime_slots'),


    path('view-patients/', ViewPatients, name='ViewPatients_d'),
    path('view-patients-records/<str:patient_id>', ViewPatientsRecords, name='ViewPatientsRecords'),

    path('actions-appointment/', Action_Appointment, name='Action_Appointment_from_Doc'),


    path('message/', message, name='message'),

    
    # Specific conversation view
    path('msg/<int:conversation_id>/', conversation_view, name='conversation_view'),
    
    # Send message
    path('<int:conversation_id>/send/', send_message, name='send_message'),
    
    # Check for new messages
    path('msg/<int:conversation_id>/check/', check_new_messages, name='check_new_messages'),
    
    # Start new conversation
    path('start/', start_conversation, name='start_conversation'),
    
    # Search conversations
    path('search/', search_conversations, name='search_conversations'),


    path('profile/', d_profile, name='profile'),
]
