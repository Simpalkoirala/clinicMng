from django.shortcuts import render, redirect, get_object_or_404 
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
import magic  # python-magic-bin for mimetype detection 

from django.contrib.auth.models import User
from django.http import HttpRequest


from account.views import login_required_with_message
from django.contrib import messages
from datetime import datetime

from account.models import Profile, MedicalInfo
from doctor.models import DoctorProfile, AppointmentDateSlot, AppointmentTimeSlot
from patient.models import *
from django.urls import reverse

from django.core.serializers.json import DjangoJSONEncoder
import json

# Constants
ALLOWED_FILE_TYPES_APPOINTMENT = [
            # Documents
            'application/pdf',
            'application/msword', # .doc
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document', # .docx
            'text/plain', # .txt

             # Images
            'image/jpeg',
            'image/png',
            'image/jpg',
            'image/gif',
            'image/webp',

             # Audio
            'audio/mpeg',  # .mp3
            'audio/wav',
            'audio/ogg',

            # Video
            'video/mp4',
            'video/ogg',
            'video/webm'
        ]

ALLOWED_FILE_TYPES_DOC = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/jpg',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]
MAX_FILE_SIZE_MB = 5

def is_valid_file(uploaded_file, allowed_file_types=ALLOWED_FILE_TYPES_DOC, max_file_size_mb=MAX_FILE_SIZE_MB):
    if not uploaded_file:
        return False, _("No file uploaded.")

    # Check size
    if uploaded_file.size > max_file_size_mb * 1024 * 1024:
        return False, _(f"File size exceeds {max_file_size_mb} MB.")

    # Check file type using content sniffing
    file_type = magic.from_buffer(uploaded_file.read(2048), mime=True)
    uploaded_file.seek(0)  # reset file pointer after reading
    if file_type not in allowed_file_types:
        return False, _("Unsupported file type.")

    return True, None








# --------------------------------------- Rendering Pages ------------------------------------------------------------


def patientDashboard(request: HttpRequest):
    return render(request, 'pages/patient/dashboard.html')



@login_required_with_message(login_url='account:login', message="You need to log in to access Profile page.")
def viewAppoinment(request: HttpRequest):  
    profile: Profile = Profile.objects.get(user=request.user)
    appointments: Appointment = Appointment.objects.filter(profile=profile).order_by('-created_at')

    context = {
        'profile': profile,
        'appointments': appointments,
    }
    return render(request, 'pages/patient/view_appoinment.html', context) 


@login_required_with_message(login_url='account:login', message="You need to log in to access Profile page.")
def BookAppoinment(request: HttpRequest):
    """Doctor booking page."""

    if request.method == 'GET':
        # Fetch the user's profile information
        profile: Profile = Profile.objects.get(user=request.user)
        doctors: DoctorProfile = DoctorProfile.objects.all()

        doctor_data = []
        for doc in doctors:
            date_slots = AppointmentDateSlot.objects.filter(doctor=doc)
            date_json = {}
            for each_date_slot in date_slots:
                date_str = each_date_slot.date.strftime('%Y-%m-%d')

                times_slots = AppointmentTimeSlot.objects.filter(appointment_date_slot=each_date_slot)
                for each_time_slot in times_slots:
                    time_str = f"{each_time_slot.from_time.strftime('%H:%M')} -- {each_time_slot.to_time.strftime('%H:%M')}"
                    all_selected_types = list(each_time_slot.appointment_type)

                    if not each_time_slot.is_booked:
                        date_json[date_str] = {
                            time_str: [each_time_slot.id, each_time_slot.duration, all_selected_types]
                        }
            doctor_data.append({
                'id': doc.id,
                'name': f"Dr. {doc.profile.user.first_name}",
                'specialty': doc.get_specialization_display(),
                'experience': doc.experience_years,
                'rating': float(doc.star_rating) if doc.star_rating else None,
                'reviews': doc.total_reviews,
                'fees': float(doc.fees),
                'image': doc.profile.profile_pic.url,
                'availability': date_json,
            })

        context = {
            'profile': profile,
            'doctors': doctors,
            'doctor_data_json': json.dumps(doctor_data, cls=DjangoJSONEncoder)
        }

        return render(request, 'pages/patient/book_appoinment.html', context)

    elif request.method == 'POST':
        try:
            # Fetch the user's profile information
            profile: Profile = Profile.objects.get(user=request.user)

            # Get the selected doctor and appointment details from the form
            doctor_id = request.POST.get('doctor_id')
            appointment_type = request.POST.get('appointment_type')
            appointment_date = request.POST.get('appointment_date')
            appointment_time = request.POST.get('appointment_time')
            appointment_time_slot_id = request.POST.get('appointment_time_id')
            appointment_reason = request.POST.get('appointment_reason', '').strip()

            appointment_file = request.FILES.get('appointment_file')

            # Fetch the doctor and date slot objects
            doctor: DoctorProfile = get_object_or_404(DoctorProfile, id=doctor_id)
            time_slot_instance: AppointmentTimeSlot = get_object_or_404(AppointmentTimeSlot, id=appointment_time_slot_id)

            time_slot_instance.is_booked = True
            time_slot_instance.save()   
            print(f"Time slot booked: {appointment_date}")
            appointment_date_foramt = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            # Create a new appointment
            appointment = Appointment.objects.create(
                profile=profile,
                doctor=doctor,
                time_slot=time_slot_instance,

                appointment_type=appointment_type,
                appointment_date=appointment_date_foramt,
                appointment_time_str=appointment_time,

                reason = appointment_reason,
                status='Pending',
            )

            if appointment_file:
                is_valid, error_msg = is_valid_file(appointment_file, ALLOWED_FILE_TYPES_APPOINTMENT, 20)
                if not is_valid:
                    messages.error(request, error_msg)
                    return JsonResponse({'error': error_msg})
                appointment.file = appointment_file
                appointment.save()

            messages.success(request, _("Appointment booked successfully."))
            return JsonResponse({'success': True, 'redirect_url': reverse('patient:viewAppoinment')})
        except Exception as e:
            messages.error(request, _("An error occurred while booking the appointment."))
            error_msg = str(e)
            print(f"Error: {error_msg}")
        return JsonResponse({'error': error_msg})

    return redirect('patient:BookAppoinment')

@login_required_with_message(login_url='account:login', message="You need to log in to access Profile page.")
def ViewDocument(request: HttpRequest):
    path = reverse('patient:ViewDocument')
    if request.method == 'POST':
        nick_name = request.POST.get('nick_name', '').strip()
        doc_type = request.POST.get('doc_type', '').strip()
        notes = request.POST.get('notes', '').strip()
        uploaded_file = request.FILES.get('document_file')

        if not nick_name or not doc_type:
            messages.error(request, "Please fill in all required fields.")
            return redirect(path+ '#add_new')

        is_valid, error_msg = is_valid_file(uploaded_file)
        if not is_valid:
            messages.error(request, error_msg)
            return redirect(path+'#add_new')
        try:
            profile: Profile = request.user.profile
            Documents.objects.create(
                profile=profile,
                nick_name=nick_name,
                doc_type=doc_type,
                notes=notes,
                file=uploaded_file,
            )
            messages.success(request, "Document uploaded successfully.")
        except Exception as e:
            messages.error(request, "An error occurred while saving the document.")
            return redirect(path+'#add_new')


        return redirect('patient:ViewDocument')
    


    profile: Profile = Profile.objects.get(user=request.user)
    documents: Documents = Documents.objects.filter(profile= profile).order_by('-created_at')
    context= {
        'profile': profile,
        'documents' : documents
    }
    return render(request, 'pages/patient/view_document.html', context)

def delete_document(request, doc_id):
    try:
        document = get_object_or_404(Documents, id=doc_id)
        
        # Optional: Only allow delete on POST
        if request.method == "POST":
            if document.file:
                document.file.delete(save=False)  # Delete file from storage
            document.delete()  # Delete record from DB
            return redirect('patient:ViewDocument')  # Redirect to your document list page
    except Documents.DoesNotExist:
        messages.error(request, "Document not found.")
    except Exception as e:  
        messages.error(request, f"An error occurred: {e}")

    # If accessed via GET, redirect to same page (or show a confirm page optionally)
    return redirect('patient:ViewDocument')



def join_v_call(request: HttpRequest):
    return render(request, 'pages/patient/join-v-call.html')

def message(request: HttpRequest):
    return render(request, 'pages/patient/message.html')

def labReport(request: HttpRequest):
    return render(request, 'pages/patient/lab_report.html')

def prescriptions(request: HttpRequest):
    return render(request, 'pages/patient/prescriptions.html')

@login_required_with_message(login_url='account:login', message="You need to log in to access Profile page.")
def p_profile(request: HttpRequest):
    """Patient profile page view."""

    if request.method == 'GET':
        # Fetch the user's profile information
        profile: Profile = Profile.objects.get(user=request.user)

        # Pass the profile information to the template
        context = {
            'profile': profile,
        }

        return render(request, 'pages/patient/profile.html', context)
    
    else:
        try:
            profile: Profile = request.user.profile
            user: User = request.user

            # Handle profile picture
            profile_pic = request.FILES.get('profileImage')  
            if profile_pic:
                profile.profile_pic = profile_pic

            # Personal Info
            user.first_name = request.POST.get('full_name', '').strip()
            # user.email = request.POST.get('email', '').strip()
            profile.ph_number = request.POST.get('phone_number', '').strip()
            profile.address = request.POST.get('address', '').strip()

            dob_str = request.POST.get('date_of_birth', '').strip()
            if dob_str:
                try:
                    profile.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
                except ValueError:
                    messages.error(request, "Invalid date format for Date of Birth.")
                    return redirect('patient:profile')

            # Medical Info
            medical_info, created = MedicalInfo.objects.get_or_create(profile=profile)
            medical_info.blood_group = request.POST.get('blood_group', '').strip()
            medical_info.medical_conditions = request.POST.get('medicalConditions', '').strip()  # fixed name
            medical_info.allergies = request.POST.get('allergies', '').strip()  # make sure this field exists
            medical_info.on_going_medications = request.POST.get('medicines_on', '').strip()  # make sure this field exists

            # Emergency Contact
            medical_info.emg_contact_name = request.POST.get('emergency_contact_name', '').strip()
            medical_info.emg_contact_number = request.POST.get('emergency_contact_number', '').strip()
            medical_info.emg_contact_relation = request.POST.get('emergency_contact_relationship', '').strip()
            medical_info.emg_contact_address = request.POST.get('emergency_contact_address', '').strip()

            # Notification Settings
            profile.email_notification = 'emailNotifications' in request.POST
            profile.reminders = 'appointmentReminders' in request.POST


            medical_info.save()
            request.user.save()
            profile.save()

            messages.success(request, "Profile updated successfully.")
        except Exception as e:
            print(f"Error updating profile: {e}")
            messages.error(request, "An error occurred while updating your profile.")

        return redirect('patient:profile')






# --------------------------------------- Adding Logic on each pages ------------------------------------------------------------

