from django.shortcuts import render, redirect, get_object_or_404
from doctor.models import *
from account.models import *
from patient.models import Appointment
from datetime import datetime, date
from datetime import timedelta, time
from collections import defaultdict
from django.contrib import messages

from django.http import JsonResponse
import json
from django.utils import timezone

from django.core.serializers.json import DjangoJSONEncoder
from account.views import login_required_with_message
from django.http import HttpRequest, HttpResponse

import uuid
from django.utils.translation import gettext as _

from home.send_email import send_custom_email
import uuid
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
DOMAIN_NAME = settings.DOMAIN_NAME


@login_required_with_message(login_url='account:login', message="You need to log in to Access Doctor Dashboard.", only=['doctor'])
def doctorDashboard(request):
    profile = request.user.profile
    doctor = DoctorProfile.objects.get(profile=profile)
    today = timezone.now().date()
    
    # Get all appointments for this doctor
    all_appointments = Appointment.objects.filter(
        doctor=doctor
    ).select_related('profile', 'profile__user', 'time_slot')
    
    # Prepare the appointment data for the template
    appointment_data = []
    for appointment in all_appointments:
        appointment_data.append({
            'id': str(appointment.uuid),
            'patient_first_name': appointment.profile.user.first_name,
            'patient_last_name': appointment.profile.user.last_name,
            'appointment_date': appointment.appointment_date.isoformat(),
            'appointment_time_str': appointment.appointment_time_str,
            # Extract hour as integer for easier grouping
            'hour': int(appointment.appointment_time_str.split(':')[0]),
            'appointment_type': appointment.appointment_type,
            'status': appointment.status,
            'reason': appointment.reason,
            'file': appointment.file.url if appointment.file and hasattr(appointment.file, 'url') else None
        })
    
    # Get all unique hours that have appointments
    all_hours = set()
    for appointment in appointment_data:
        if 'hour' in appointment:
            all_hours.add(appointment['hour'])
    
    # Generate hour list sorted (for timeline view)
    hour_list = sorted(list(all_hours)) if all_hours else [f"{h}" for h in range(8, 20)]
    
    # Get the week's dates (for weekly view)
    week_dates = []
    start_of_week = today - timedelta(days=today.weekday())
    for i in range(7):
        week_dates.append((start_of_week + timedelta(days=i)).isoformat())
    
    # Get counts for summary section
    today_count = all_appointments.filter(appointment_date=today).count()
    confirmed_count = all_appointments.filter(status='confirmed').count()
    pending_count = all_appointments.filter(status='pending').count()
    week_end = today + timedelta(days=7)
    week_count = all_appointments.filter(appointment_date__gte=today, appointment_date__lte=week_end).count()
    
    # Serialize to JSON here to avoid template issues
    appointment_json = json.dumps(appointment_data, cls=DjangoJSONEncoder)
    week_dates_json = json.dumps(week_dates)
    
    context = {
        'all_appointments_json': appointment_json,  # Send the serialized JSON
        'hour_list': hour_list,
        'week_dates_json': week_dates_json,
        'today': today.isoformat(),
        'today_count': today_count,
        'confirmed_count': confirmed_count,
        'pending_count': pending_count,
            'week_count': week_count,

        'counts': {
            'total_patients': all_appointments.count(),
            'pending_patients': all_appointments.filter(status='pending').count(),
            'todays_appointments': all_appointments.filter(appointment_date=date.today()).count(),
        },
    }
    
    return render(request, 'pages/doctor/dashboard.html', context)

@login_required_with_message(login_url='account:login', message="You need to log in to Manage the session.", only=['doctor'])
def SessionMng(request):
    if request.method == 'GET':     
        profile: Profile = request.user.profile
        doctor: DoctorProfile = DoctorProfile.objects.get(profile=profile)
    
    
        today = timezone.localdate()
        all_appointment = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date')
        context = {
            'doctor': doctor,
            'todays_appointments': all_appointment.filter(appointment_date=date.today(), status='confirmed'),
        }
        return render(request, 'pages/doctor/schedule_mng.html', context)
    
    elif request.method == 'POST':
        app_id = request.POST.get('appoint_Id')
        slot_id = request.POST.get('slotId')

        if not app_id or not slot_id:
            messages.error(request, "Incomplete Data.")
            return redirect('doctor:SessionMng')
        
        try:
            appointment = Appointment.objects.get(uuid=app_id)
            new_slot = AppointmentTimeSlot.objects.get(unique_id=slot_id)
        except (Appointment.DoesNotExist, AppointmentTimeSlot.DoesNotExist):
            messages.error(request, "Appointment or slot not found.")
            return redirect('doctor:SessionMng')

        # Assign the new new_slot to the appointment
        new_date_slot = new_slot.appointment_date_slot

        appointment.time_slot = new_slot
        appointment.appointment_date = new_date_slot.date
        time_str = f"{new_slot.from_time.strftime('%H:%M')} -- {new_slot.to_time.strftime('%H:%M')}"
        appointment.appointment_time_str = time_str

        appointment.appointment_type = new_slot.appointment_type[0] if new_slot.appointment_type else 'general_consultation'
        appointment.status = 'pending'  # Reset status to pending or as needed
        appointment.save()

        # Optionally, update new_slot status if needed
        new_slot.status = 'booked'
        new_slot.save()

        # Check if a conversation already exists between the patient and doctor
        existing_conversation: Conversation = Conversation.objects.filter(
            participants=appointment.doctor.profile
        ).filter(
            participants=appointment.profile
        ).distinct().first()
        
        # Only create new conversation if one doesn't exist
        if not existing_conversation:
            conversation = Conversation.objects.create(
                uuid=uuid.uuid4(),
                status='initiated',
            )
            conversation.participants.add(appointment.profile, appointment.doctor.profile)
            conversation.save()
            existing_conversation = conversation

        Message.objects.create(
            conversation=existing_conversation,
            sender=appointment.profile,
            content=f"Appointment with Dr. {appointment.doctor.profile.user.get_full_name()} has been rescheduled to {appointment.appointment_date} at {time_str}.",
            message_type = "appoinment"  # This is a normal message, not a call request
        )

        # send email notification to patient
        send_custom_email(
            subject=f"Appointment Rescheduled: {appointment.appointment_type}",
            message=f"Your appointment has been rescheduled to {appointment.appointment_date} at {time_str}.",
            recipient_list=[appointment.profile.user.email]
        )

        messages.success(request, "Appointment slot updated successfully.")
        return redirect('doctor:SessionMng')


def reschedule_appointment(request):
    """
    Reschedule an appointment to a new time slot.
    """
    try:
        data = json.loads(request.body)
        app_id = data.get('appoint_Id')
        new_slot_id = data.get('new_slot_id')
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    print(f"Rescheduling appointment {app_id} to new slot {new_slot_id}")


    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        appointment = Appointment.objects.get(uuid=app_id)
    except Appointment.DoesNotExist:
        return JsonResponse({'error': 'Appointment not found'}, status=404)

    if not new_slot_id:
        return JsonResponse({'error': 'New slot ID is required'}, status=400)

    try:
        new_slot = AppointmentTimeSlot.objects.get(unique_id=new_slot_id)
    except AppointmentTimeSlot.DoesNotExist:
        return JsonResponse({'error': 'New slot not found'}, status=404)

    # Update the appointment with the new slot
    appointment.time_slot = new_slot
    appointment.appointment_date = new_slot.appointment_date_slot.date
    time_str = f"{new_slot.from_time.strftime('%H:%M')} -- {new_slot.to_time.strftime('%H:%M')}"
    appointment.appointment_time_str = time_str
    appointment.appointment_type = new_slot.appointment_type[0] if new_slot.appointment_type else 'general_consultation'
    appointment.status = 'pending'  # Reset status to pending or as needed
    appointment.save()

    # Optionally, update new_slot status if needed
    new_slot.status = 'booked'
    new_slot.save()

    messages.success(request, "Appointment rescheduled successfully.")
    
    return JsonResponse({'success': True, 'message': 'Appointment rescheduled successfully.'})

@login_required_with_message(login_url='account:login', message="You need to log in to Doctor Data.", only=['doctor'])
def get_doctor_availability_json(request, app_uuid):
    """
    Returns available slots (not booked or unavailable) for the given doctor as JSON.
    """
    try:
        appointment = Appointment.objects.get(uuid=app_uuid)
        doc = appointment.doctor
    except Appointment.DoesNotExist:
        return JsonResponse({'error': 'Url Missmatch'}, status=404)

    today = timezone.localdate()
    date_slots = AppointmentDateSlot.objects.filter(doctor=doc, date__gte=today)

    date_json = {}
    for each_date_slot in date_slots:
        date_str = each_date_slot.date.strftime('%Y-%m-%d')
        times_slots = AppointmentTimeSlot.objects.filter(appointment_date_slot=each_date_slot)
        for each_time_slot in times_slots:
            if each_time_slot.status not in ['booked', 'unavailable', 'break']:
                time_str = f"{each_time_slot.from_time.strftime('%H:%M')} -- {each_time_slot.to_time.strftime('%H:%M')}"
                all_selected_types = list(each_time_slot.appointment_type)
                if date_str not in date_json:
                    date_json[date_str] = {}
                date_json[date_str][time_str] = [
                    each_time_slot.unique_id, each_time_slot.duration, all_selected_types
                ]
    
    
    return JsonResponse({'availability': date_json})


@login_required_with_message(login_url='account:login', message="You need to log in to Edit Date Schedules.", only=['doctor'])
def d_edit_schedules(request):
    profile: Profile = request.user.profile
    doctor: DoctorProfile = DoctorProfile.objects.get(profile=profile)
    date_slots = AppointmentDateSlot.objects.filter(doctor=doctor).order_by('date')

    context = {
        'doctor' : doctor,
        'all_date_slots': date_slots
    }
    return render(request, 'pages/doctor/edit_schedules.html', context)

@login_required_with_message(login_url='account:login', message="You need to log in to Edit Date Schedules.", only=['doctor'])
def get_dateTime_slots(request, start_date=None):
    profile: Profile = request.user.profile
    doctor: DoctorProfile = DoctorProfile.objects.get(profile=profile)
    date_slots = AppointmentDateSlot.objects.filter(doctor=doctor).order_by('date')
    Message = None
    # Parse start_date from string if provided, else use today
    if start_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            Message = "Invalid date format. Please use YYYY-MM-DD. For Now set start_date to today."
            start_date = date.today()
    else:
        start_date = date.today()

    date_range = [start_date + timedelta(days=i) for i in range(7)]

    # Preload all time slots for performance
    time_slots_all = AppointmentTimeSlot.objects.filter(
        appointment_date_slot__in=date_slots
    ).select_related('appointment_date_slot')

    # Map: { date: { hour: slot_data } }
    slot_lookup = defaultdict(dict)
    for ts in time_slots_all:
        date_str = ts.appointment_date_slot.date.strftime("%Y-%m-%d")
        hour = ts.from_time.hour
        slot_lookup[date_str][hour] = {
            'unique_id': ts.unique_id,
            'blank': 'false',
            'hour': hour,
            'from_time': ts.from_time.strftime("%H:%M"),
            'to_time': ts.to_time.strftime("%H:%M"),
            'duration': ts.duration,
            'appointment_type': ts.appointment_type,
            'status': ts.status,
        }

    # Construct output
    appointment_data = {}
    for each_date in date_range:
        date_str = each_date.strftime("%Y-%m-%d")
        appointment_data[date_str] = []

        for hour in range(8, 22):  # 8 to 21 inclusive
            slot_data = slot_lookup.get(date_str, {}).get(hour, {
                'unique_id': '',
                'blank': 'true',
                'hour': hour,
                'from_time': f"{hour}:00",
                'to_time': f"{hour + 1}:00",
                'duration': '30',  # default duration
                'appointment_type': 'General Checkup',  # default type
                'status': 'unavailable',  # default
            })
            appointment_data[date_str].append(slot_data)

    return JsonResponse({
        "success": True,
        "message": Message,
        "scheduleData": appointment_data
    }, safe=False)

@login_required_with_message(login_url='account:login', message="You need to log in to Access Doctor Dashboard.", only=['doctor'])
def submit_dateTime_slots(request):
    if request.method != 'POST':
        return JsonResponse({'success': False,
                             'message': 'Only POST requests allowed'}, 
                             status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    
    profile: Profile = request.user.profile
    doctor: DoctorProfile = DoctorProfile.objects.get(profile=profile)

    for date_str, slots in data.items():
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue  # skip invalid dates
        
        # Find or create date slot

        for slot in slots:
            # Skip if slot is already booked
            if slot.get('status') == 'booked':
                continue

            # Skip if slot is blank and remains unavailable (no need to update)
            if slot.get('blank') == 'true' and slot.get('status') == 'unavailable':
                continue

            date_slot, _ = AppointmentDateSlot.objects.get_or_create(doctor=doctor, date=date_obj)
            hour = slot.get('hour')
            status = slot.get('status', 'unavailable')
            duration = int(slot.get('duration', 30))

            # Time boundaries (duration is in minutes)
            from_time = time(hour, 0)
            to_time = (datetime.combine(date_obj, from_time) + timedelta(minutes=duration)).time()

            # Check if slot already exists
            existing_slot = AppointmentTimeSlot.objects.filter(
                appointment_date_slot=date_slot,
                from_time=from_time,
                to_time=to_time
            ).first()

            if existing_slot:
                # Update existing
                existing_slot.status = status
                existing_slot.duration = str(duration)
                existing_slot.save()
            else:
                # Create new
                AppointmentTimeSlot.objects.create(
                    appointment_date_slot=date_slot,
                    from_time=from_time,
                    to_time=to_time,
                    duration=str(duration),
                    status=status
                )


    return JsonResponse({'success': True, 'message': 'Schedule updated successfully'})



@login_required_with_message(login_url='account:login', message="You need to log in to view your Patient Details .", only=['doctor'])
def ViewPatients(request):
    profile: Profile = request.user.profile
    doctor: DoctorProfile = DoctorProfile.objects.get(profile = profile)


    all_appoinemts: Appointment = Appointment.objects.filter(doctor = doctor)


    patientData= []

    for each_app in all_appoinemts:
        each_app: Appointment

        dob = each_app.profile.date_of_birth
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        patientData.append({
            "id": str(each_app.uuid),
            "image": each_app.profile.profile_pic.url,
            "name": each_app.profile.user.first_name,
            "patient_id": each_app.profile.user.username,
            "age": age,
            "gender": each_app.profile.gender,
            "appointment": each_app.appointment_date.strftime("%Y-%m-%d") + each_app.appointment_time_str ,
            "status": each_app.status ,
            "issue": each_app.appointment_type,
            "phone": each_app.profile.ph_number ,
            "email": each_app.profile.user.email ,
            "notes": each_app.reason,
            "file": each_app.file.url if each_app.file else ''

        })


    context = {
        "patientData": patientData
    }

    return render(request, 'pages/doctor/view_appointments.html', context)


@login_required_with_message(login_url='account:login', message="You need to log in to Change the Status.", only=['doctor'])
def Action_Appointment(request):
    if request.method != 'POST':
        return JsonResponse({'success': False,
                             'message': 'Only POST requests allowed'}, 
                             status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    profile: Profile = request.user.profile
    doctor: DoctorProfile = DoctorProfile.objects.get(profile=profile)

    app_id = data.get('app_id')
    action = data.get('action')
    

    appointment: Appointment = Appointment.objects.get(uuid=app_id)

    if action == 'confirm' or action == 'confirmed':
        appointment.status = 'confirmed'
        appointment.confirm_by = doctor.profile
        appointment.save()
    elif action == 'cancel' or action == 'cancelled':
        appointment.status = 'cancelled'
        appointment.cancled_by = doctor.profile
        appointment.cancel_reason = request.POST.get('cancel_reason', '')
        appointment.save()

    elif action == 'complete' or action == 'completed':
        appointment.status = 'completed'
        appointment.completed_by = doctor.profile
        appointment.save()

    # Prepare email details
    appointment_date = appointment.appointment_date.strftime("%Y-%m-%d")
    appointment_time = appointment.appointment_time_str
    patient_name = appointment.profile.user.get_full_name()
    doctor_name = doctor.profile.user.get_full_name()
    status_display = appointment.status.capitalize()

    if action in ['confirm', 'confirmed']:
        subject = f"Appointment Confirmed"
        message = (
            f"Dear {patient_name},\n\n"
            f"Your appointment has been confirmed by Dr. {doctor_name}.\n"
            f"Date: {appointment_date}\n"
            f"Time: {appointment_time}\n"
            f"Type: {appointment.appointment_type}\n"
            f"Status: {status_display}\n\n"
            f"Thank you for choosing our clinic."
        )
    elif action in ['cancel', 'cancelled']:
        subject = f"Appointment Cancelled"
        message = (
            f"Dear {patient_name},\n\n"
            f"Your appointment scheduled on {appointment_date} at {appointment_time} has been cancelled by Dr. {doctor_name}.\n"
            f"Reason: {getattr(appointment, 'cancel_reason', '')}\n"
            f"Status: {status_display}\n\n"
            f"If you have any questions, please contact us."
        )
    elif action in ['complete', 'completed']:
        subject = f"Appointment Completed"
        message = (
            f"Dear {patient_name},\n\n"
            f"Your appointment with Dr. {doctor_name} on {appointment_date} at {appointment_time} has been marked as completed.\n"
            f"Status: {status_display}\n\n"
            f"Thank you for visiting our clinic."
        )
    else:
        subject = f"Appointment Status Updated"
        message = (
            f"Dear {patient_name},\n\n"
            f"Your appointment status has been updated to {status_display} by Dr. {doctor_name}.\n"
            f"Date: {appointment_date}\n"
            f"Time: {appointment_time}\n"
            f"Type: {appointment.appointment_type}\n\n"
            f"Thank you."
        )


    # Check if a conversation already exists between the patient and doctor
    existing_conversation: Conversation = Conversation.objects.filter(
        participants=appointment.doctor.profile
    ).filter(
        participants=appointment.profile
    ).distinct().first()
    
    # Only create new conversation if one doesn't exist
    if not existing_conversation:
        conversation = Conversation.objects.create(
            uuid=uuid.uuid4(),
            status='initiated',
        )
        conversation.participants.add(appointment.profile, appointment.doctor.profile)
        conversation.save()
        existing_conversation = conversation

    Message.objects.create(
        conversation=existing_conversation,
        sender=appointment.profile,
        content=message,
        message_type = "appoinment"  # This is a normal message, not a call request
    )


    send_custom_email(
        subject=subject,
        message=message,
        recipient_list=[appointment.profile.user.email, doctor.profile.user.email]
    )
    return JsonResponse({'success': True, 'message': f'Appointment {action}ed successfully'})



@login_required_with_message(login_url='account:login', message="You need to log in to view your Profile.", only=['doctor'])
def d_profile(request):
    profile: Profile = request.user.profile
    context = {
            'profile': profile,
    }
    return render(request, 'pages/doctor/profile.html', context)


@login_required_with_message(login_url='account:login', message="You need to log in to view your Messages.", only=['doctor'])
def message(request):
    profile : Profile = request.user.profile

    conversations = Conversation.objects.filter(
        participants=profile
    )

    connected_paritcipants = []
    
    # Add additional data to each conversation
    for conversation in conversations:
        # Get the other participant (not the current user)
        conversation.other_participant = conversation.participants.exclude(
            id=profile.id
        ).first()

        if conversation.other_participant:
            connected_paritcipants.append(conversation.other_participant)
        
        # Get the last message
        conversation.last_message = conversation.messages.last()
        # Check if there are unread messages
        conversation.has_unread = conversation.messages.filter(
            read=False
        ).exclude(sender=profile).exists()

    # # Mark messages as read
    # conversation.messages.filter(
    #     read=False
    # ).exclude(sender=profile).update(read=True)

    # messages_list = conversation.messages.all().order_by('timestamp')
    # concept_data = {'active_conversation_id': conversation.id,
    #     'active_conversation': conversation,
    #     'message_lists': messages_list,}




    # Get all other not connected participants excluding the current user
    connected_ids = [p.id for p in connected_paritcipants]
    connected_ids.append(profile.id)
    if profile.role == 'doctor':
        not_connected_usr = Profile.objects.exclude(id__in=connected_ids).filter(role='patient')
    else:
        not_connected_usr = Profile.objects.exclude(id__in=connected_ids).filter(role='doctor')

    context = {
        'profile': profile,
        'conversations': conversations,
        'not_connected_usr': not_connected_usr,
        # 'active_conversation_id': conversation.id,
        # 'active_conversation': conversation,
        # 'message_lists': messages_list,
    }

    return render(request, 'pages/doctor/message.html', context)



# video call views
@login_required_with_message(login_url='account:login', message="You need to log in to view your Video Calls.", only=['doctor'])
def view_v_call(request: HttpRequest):
    """Request a video call with a doctor."""
    if request.method != 'POST':
        profile: Profile = request.user.profile
      
        convs =  Conversation.objects.filter(
            participants=request.user.profile
        ).order_by('-created_at')
        for conversation in convs:
            # Get the other participant (not the current user)
            conversation.other_participant = conversation.participants.exclude(
                id=profile.id
            ).first()

    return render(request, 'pages/doctor/list-v-call.html',{ 'conv': convs,}  )

@login_required_with_message(login_url='account:login', message="You need to log in to Send Call Request.", only=['doctor'])
def send_req_calls(request: HttpRequest, convo_uuid: uuid):
    """Send a request for a video call."""
    try:
        profile: Profile = request.user.profile
        conversation: Conversation = get_object_or_404(Conversation, uuid=convo_uuid)

        # Ensure the user is part of the conversation
        if profile not in conversation.participants.all():
            messages.error(request, _("You are not part of this conversation."))
            return redirect('doctor:view_v_call')

        # create a call object
        call = Calls.objects.create(
            uuid=uuid.uuid4(),
            connection=conversation,
            caller=profile,
            last_req=timezone.now(),
            status='requested',
            receiver=conversation.participants.exclude(id=profile.id).first()
        )
 
        Message.objects.create(
            conversation=conversation,
            sender=profile,
            content=f"Call Request from {profile.user.first_name}",
            message_type = "call"  # Mark this message as a call request
        )

        if call.receiver.role == "patient":
            #send Mail for patient
            send_custom_email(
                    subject=f"Call Request, From: DR. {call.caller.user.first_name}",
                    message=f"Hi, The Call was Requested. \n\nFrom: Dr. {call.caller.user.first_name}  \nTo: {call.receiver.user.first_name} \n\nPlz Get Free And Join a Call      \n\n\n#{DOMAIN_NAME}/p/join-v-call/{call.uuid}/ ",
                    recipient_list=[call.caller.user.email]
            )
        elif call.receiver.role == "doctor":
            #send Mail for Doctor
            send_custom_email(
                    subject=f"Call Request, From: {call.caller.user.first_name} ",
                    message=f"Hi, The Call was Requested. \n\nFrom: {call.caller.user.first_name}  \nTo: Dr.{call.receiver.user.first_name} \n\nPlz Get Free And Join a Call      \n\n\n#{DOMAIN_NAME}/d/join-v-call/{call.uuid}/ ",
                    recipient_list=[call.caller.user.email]
            )

        messages.success(request, _("Video call request sent successfully."))
        return redirect('doctor:join_v_call', calls_uuid=call.uuid)
    except Exception as e:
        print(f"Error: {e}")
        messages.error(request, _("An error occurred while sending the video call request."))
        return redirect('doctor:view_v_call')

@login_required_with_message(login_url='account:login', message="You need to log in to Join your Video Calls.", only=['doctor'])
def join_v_call(request: HttpRequest, calls_uuid: uuid):

    profile: Profile = request.user.profile
    calls: Calls = get_object_or_404(Calls, uuid=calls_uuid)

    # Ensure the call exists, completed or cancelled calls cannot be joined
    if calls.status not in ['requested', 'active', 'ongoing']:
        messages.error(request, _("The call cannot be joined as it is either completed or cancelled."))
        return redirect('doctor:view_v_call')

    conversation: Conversation = calls.connection

    # Ensure the user is part of the conversation
    if profile not in conversation.participants.all():
        messages.error(request, _("You are not part of this conversation."))
        return redirect('doctor:view_v_call')
    
    conversation.other_participant = conversation.participants.exclude(
        id=profile.id
    ).first()

    is_caller = calls.caller == profile

    # Check if the user is joining for the first time or rejoining
    last_call_message = conversation.messages.filter(message_type="call").order_by('-timestamp').first()
    if not last_call_message or (timezone.now() - last_call_message.timestamp).total_seconds() > 60000000:
        # Send email notification if it's been more than 6 minutes since the last call-related message
        send_custom_email(
            subject=f"Call Request, From: {calls.caller.user.first_name}",
            message=f"Hi, The Call was Requested. \n\nFrom: {calls.caller.user.first_name}  \nTo: Dr.{calls.receiver.user.first_name} \n\nPlz Get Free And Join a Call      \n\n\n#{DOMAIN_NAME}/d/join-v-call/{calls.uuid}/ ",
            recipient_list=[calls.receiver.user.email]
        )
        message_content = f"{profile.user.first_name} has joined the call."
    else:
        message_content = f"{profile.user.first_name} has rejoined the call."

    # Create a message indicating the user has joined or rejoined
    Message.objects.create(
        conversation=conversation,
        sender=profile,
        content=message_content,
        message_type="call"  # Mark this message as a call-related message
    )

    return render(request, 'pages/doctor/join-v-call.html', {'conversation': conversation,
                                                                'call_obj': calls,
                                                                'is_caller': is_caller,})

@login_required_with_message(login_url='account:login', message="You need to log in to Enter Waiting Room.", only=['doctor'])
def waiting_room(request: HttpRequest, calls_uuid: uuid):
    """Join a video call with a specific conversation ID."""
    profile: Profile = request.user.profile
    calls: Calls = get_object_or_404(Calls, uuid=calls_uuid)
    conversation: Conversation = calls.connection

    # Ensure the user is part of the conversation
    if profile not in conversation.participants.all():
        messages.error(request, _("You are not part of this conversation."))
        return redirect('doctor:view_v_call')
    

    conversation.other_participant = conversation.participants.exclude(
        id=profile.id
    ).first()
    
    return render(request, 'pages/patient/waiting-room.html', {'conversation': conversation,
                                                                'call_obj': calls,})


@csrf_exempt
def submit_notes(request: HttpRequest):
    """Submit notes for an appointment via AJAX request."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Only POST requests are allowed.'}, status=405)

    try:
        call_uuid = request.POST.get('call_uuid', None)
        quick_notes = request.POST.get('quick_notes', '').strip()
        lab_report_notes = request.POST.get('lab_report_notes', '').strip()
        prescription_notes = request.POST.get('prescription_notes', '').strip()

        if not call_uuid:
            return JsonResponse({'success': False, 'message': 'Call UUID is required.'}, status=400)

        call: Calls = get_object_or_404(Calls, uuid=call_uuid)
        call.quick_notes = quick_notes
        call.lab_report_notes = lab_report_notes
        call.prescription_notes = prescription_notes
        call.save()

        # Prepare the content for the message
        patient:Profile = call.connection.participants.exclude(id=request.user.profile.id).first()
        Content_msg = f"Notes have been submitted for the call with Dr.{ request.user.first_name }  &  { patient.user.first_name }\n CallID: {call_uuid}\n\n➡️Notes submitted:\n{quick_notes} \n\n ➡️Lab Reports: \n{lab_report_notes} \n\n ➡️Prescription: \n{prescription_notes} \n\n Dorctor username: {request.user.username}\n Patient username: {patient.user.username} \nPlz check Above Notes and Work on it."

        # Create a message indicating the notes have been submitted
        Message.objects.create(
            conversation=call.connection,
            sender=request.user.profile,
            content=Content_msg,
            message_type="notes"  # Mark this message as notes-related
        )

        # Also need to send a message to management profile user
        management_email = [profile.user.email for profile in Profile.objects.filter(role='management')] 
        management_profile = Profile.objects.filter(role='management')
        for management_profile in management_profile:
            if management_profile:
                # Find or create a conversation between the doctor and management
                existing_conversation: Conversation = Conversation.objects.filter(
                    participants=request.user.profile
                    ).filter(
                    participants=management_profile
                ).distinct().first()
                if not existing_conversation:
                    conversation = Conversation.objects.create(
                                uuid=uuid.uuid4(),
                                status='initiated',
                            )
                    conversation.participants.add(request.user.profile, management_profile)
                    conversation.save()
                    existing_conversation = conversation

                Message.objects.create(
                    conversation=existing_conversation,
                    sender=request.user.profile,
                    content=Content_msg,
                    message_type="notes"  # Mark this message as notes-related
                )

        # Send email notification to the doctor
        send_custom_email(
            subject=f"Notes Submitted for Call {call_uuid}",
            message=Content_msg,
            recipient_list=management_email
        )

        return JsonResponse({'success': True, 'message': 'Notes submitted successfully.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f"An error occurred: {str(e)}"}, status=500)
