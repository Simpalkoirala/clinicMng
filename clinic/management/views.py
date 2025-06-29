from django.shortcuts import render, redirect

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from patient.models import *
from account.models import Profile

from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.contrib import messages
from django.db.models import ProtectedError, Count

from datetime import datetime, date
from decimal import Decimal, InvalidOperation

from django.db import transaction

from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

from django.utils import timezone
from django.utils.timezone import now
from calendar import monthrange

from account.views import login_required_with_message


from home.send_email import send_custom_email
import uuid
from django.conf import settings
DOMAIN_NAME = settings.DOMAIN_NAME

# Create your views here.
@login_required_with_message(login_url='account:login', message="You need to log in to Access Doctor Dashboard.", only=['management'])
def management_dashboard(request):
    profile = Profile.objects.get(user=request.user)
    
    # Get the current month and year
    current_date = now()
    current_month = current_date.month
    current_year = current_date.year
    
    # Number of days in the current month
    days_in_month = monthrange(current_year, current_month)[1]
    
    # Initialize daily appointment counts
    daily_appointments = [0] * days_in_month
    emergency_appointments = [0] * days_in_month
    other_appointments = [0] * days_in_month
    
    # Retrieve appointments for the current month
    appointments_this_month = Appointment.objects.filter(
        appointment_date__month=current_month,
        appointment_date__year=current_year
    )
    
    # Populate daily appointment counts
    for appointment in appointments_this_month:
        day_index = appointment.appointment_date.day - 1
        daily_appointments[day_index] += 1
        if appointment.appointment_type == 'emergency':
            emergency_appointments[day_index] += 1
        else:
            other_appointments[day_index] += 1

    # Appointment type distribution
    appointment_type_distribution = appointments_this_month.values('appointment_type').annotate(count=Count('appointment_type'))
    appointment_types = {
        'general_consultation': 0,
        'follow_up_visit': 0,
        'online_consultation': 0,
        'offline_consultation': 0,
    }
    for item in appointment_type_distribution:
        appointment_types[item['appointment_type']] = item['count']
    
    context = {
        'profile': profile,
        'appointments': appointments_this_month.order_by('-created_at')[:5],
        'total_appointments': appointments_this_month.count(),
        'total_patients': Profile.objects.filter(role='patient').count(),
        'total_doctors': Profile.objects.filter(role='doctor').count(),
        'daily_appointments': daily_appointments,
        'emergency_appointments': emergency_appointments,
        'other_appointments': other_appointments,
        'appointment_types': appointment_types,
    }
    return render(request, 'pages/management/dashboard.html', context)

@login_required_with_message(login_url='account:login', message="You need to log in to Access Management Dashboard.", only=['management'])
def ViewAppointmnets(request):
    qs = Appointment.objects.all().order_by('-created_at')
    # pull per_page from GET, default 10
    per_page = int(request.GET.get('per_page', 10))
    paginator = Paginator(qs, per_page)
    page_num = request.GET.get('page')

    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # define your entries‑per‑page options here
    per_page_options = [10, 25, 50, 100]

    context = {
        'appointments': page_obj,
        'paginator': paginator,
        'per_page': per_page,
        'per_page_options': per_page_options,
    }

    return render(request, 'pages/management/view_appointments.html', context)


# Patient Management View
@login_required_with_message(login_url='account:login', message="You need to log in to View Patients.", only=['management'])
def ViewPatients(request):
    patients = Profile.objects.filter(role='patient').order_by('-created_at')
    

    # pull per_page from GET, default 10
    per_page = int(request.GET.get('per_page', 10))
    paginator = Paginator(patients, per_page)
    page_num = request.GET.get('page')

    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # define your entries‑per‑page options here
    per_page_options = [10, 25, 50, 100]

    context = {
        'patients': page_obj,
        'paginator': paginator,
        'per_page': per_page,
        'per_page_options': per_page_options,
    }
    return render(request, 'pages/management/view_patients.html', context)

@require_POST
@login_required_with_message(login_url='account:login', message="You need to log in to update Patient Profile.", only=['management'])
def update_profile(request, username):
    """
    View to update a patient's profile information
    """
    # Get the profile to update
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    
    try:

        if 'full_name' in request.POST:
            full_name = request.POST.get('full_name', '').strip()
            user.first_name = full_name
            user.save()

        # Handle profile picture if provided
        if 'profile_pic' in request.FILES:
            profile.profile_pic = request.FILES['profile_pic']
        
        # Update profile fields
        if 'ph_number' in request.POST:
            profile.ph_number = request.POST.get('ph_number', '')
        
        if 'address' in request.POST:
            profile.address = request.POST.get('address', '')
        
        if 'date_of_birth' in request.POST and request.POST.get('date_of_birth'):
            profile.date_of_birth = request.POST.get('date_of_birth')
        
        if 'gender' in request.POST:
            profile.gender = request.POST.get('gender', '')
        
        # Update notification settings
        profile.email_notification = 'email_notification' in request.POST
        profile.sms_notification = 'sms_notification' in request.POST
        profile.reminders = 'reminders' in request.POST

        profile.is_active = 'is_active' in request.POST
        profile.is_verified = 'is_verified' in request.POST
        
        # Save the profile
        profile.save()
        
        #Send email notification to the user
        send_custom_email(
            subject='Profile Updated',
            message=f'Dear {user.first_name},\n\nYour profile has been updated successfully.\n\nThank you!',
            recipient_list=[user.email],
        )

        # Return success response with updated data
        return JsonResponse({
            'status': 'success',
            'message': 'Profile updated successfully',
            'profile_pic_url': profile.profile_pic.url if profile.profile_pic else None
        })
        
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error updating profile: {str(e)}'
        }, status=400)

@require_POST
@login_required_with_message(login_url='account:login', message="You need to log in to update Patient Medical Information.", only=['management'])
def update_medical_info(request, username):
    """
    View to update a patient's medical information
    """
    # Check permissions (only the user themselves or staff can update)
    if request.user.username != username and not request.user.is_staff:
        return JsonResponse({
            'status': 'error',
            'message': 'You do not have permission to update this medical information'
        }, status=403)
    
    # Get the medical info to update
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    
    # Get or create medical info if it doesn't exist
    medical_info, created = MedicalInfo.objects.get_or_create(profile=profile)
    
    try:
        # Update medical info fields
        if 'blood_group' in request.POST:
            medical_info.blood_group = request.POST.get('blood_group', '')
        
        if 'allergies' in request.POST:
            medical_info.allergies = request.POST.get('allergies', '')
        
        if 'medical_conditions' in request.POST:
            medical_info.medical_conditions = request.POST.get('medical_conditions', '')
        
        if 'on_going_medications' in request.POST:
            medical_info.on_going_medications = request.POST.get('on_going_medications', '')
        
        # Update emergency contact information
        if 'emg_contact_name' in request.POST:
            medical_info.emg_contact_name = request.POST.get('emg_contact_name', '')
        
        if 'emg_contact_number' in request.POST:
            medical_info.emg_contact_number = request.POST.get('emg_contact_number', '')
        
        if 'emg_contact_relation' in request.POST:
            medical_info.emg_contact_relation = request.POST.get('emg_contact_relation', '')
        
        if 'emg_contact_address' in request.POST:
            medical_info.emg_contact_address = request.POST.get('emg_contact_address', '')
        
        # Save the medical info
        medical_info.save()
        
        send_custom_email(
            subject='Medical Information Updated',
            message=f'Dear {user.first_name},\n\nYour medical information has been updated successfully.\n\nThank you!',
            recipient_list=[user.email],
        )   

        # Return success response
        return JsonResponse({
            'status': 'success',
            'message': 'Medical information updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error updating medical information: {str(e)}'
        }, status=400)

@login_required_with_message
def create_patient(request):
    """API endpoint for creating a new patient with profile and medical info"""
    try:
        # Check if the request has multipart form data
        # Handle form data
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        password = request.POST.get('password')
        
        # Profile data
        phone = request.POST.get('phone', '')
        date_of_birth = request.POST.get('date_of_birth') or None
        gender = request.POST.get('gender', '')
        address = request.POST.get('address', '')
        profile_pic = request.FILES.get('profile_pic')
        
        # Notification preferences
        email_notification = request.POST.get('email_notification') == 'on'
        sms_notification = request.POST.get('sms_notification') == 'on'
        reminders = request.POST.get('reminders') == 'on'
        
        # Medical info
        blood_group = request.POST.get('blood_group', '')
        allergies = request.POST.get('allergies', '')
        medical_conditions = request.POST.get('medical_conditions', '')
        on_going_medications = request.POST.get('on_going_medications', '')
        
        # Emergency contact
        emg_contact_name = request.POST.get('emg_contact_name', '')
        emg_contact_number = request.POST.get('emg_contact_number', '')
        emg_contact_relation = request.POST.get('emg_contact_relation', '')
        emg_contact_address = request.POST.get('emg_contact_address', '')

        # Validate required fields
        if not all([ email, first_name, password]):
            return JsonResponse({
                'success': False,
                'message': 'Missing required fields',
                'current_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                'current_user': request.user.username
            }, status=400)
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'message': 'Email already exists',
                'current_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                'current_user': request.user.username
            }, status=400)
        # Create a new user; here username is set as the email for simplicity
        current_time = datetime.now().strftime('%Y%m%d%H%M%S')  # Format: YYYYMMDDHHMMSS
        counter = str(User.objects.count() + 1).zfill(8)  # Ensure at least 6 digits
        username = f"NCMS-{current_time}-{counter}"
        # Create user, profile, and medical info in a transaction
        with transaction.atomic():
            # Create the user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
            )
            
            # Create the profile
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'patient',
                    'ph_number': phone,
                    'date_of_birth': date_of_birth,
                    'gender': gender,
                    'address': address,
                    'email_notification': email_notification,
                    'sms_notification': sms_notification,
                    'reminders': reminders,
                    'is_verified': True,  # Auto-verify since created by staff
                    'is_active': True,  # Auto-activate since created by staff
                }
            )

            if not created:
                # If profile already exists, update it
                profile.role = 'patient'  # Ensure role is set to patient
                profile.ph_number = phone
                profile.date_of_birth = date_of_birth
                profile.gender = gender
                profile.address = address
                profile.email_notification = email_notification
                profile.sms_notification = sms_notification
                profile.reminders = reminders
                profile.is_verified = True  # Auto-verify since created by staff
                profile.is_active = True  # Auto-activate since created by staff
                profile.save()
         
            
            # Set profile picture if provided
            if profile_pic:
                profile.profile_pic = profile_pic
                profile.save()
            
            # Create medical info
            medical_info = MedicalInfo.objects.create(
                profile=profile,
                blood_group=blood_group,
                allergies=allergies,
                medical_conditions=medical_conditions,
                on_going_medications=on_going_medications,
                emg_contact_name=emg_contact_name,
                emg_contact_number=emg_contact_number,
                emg_contact_relation=emg_contact_relation,
                emg_contact_address=emg_contact_address
            )
        
        # Prepare response data
        response_data = {
            'success': True,
            'message': 'Patient registered successfully',
            'patient': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'profile_id': profile.id,
                'medical_info_id': medical_info.id
            },
            'current_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'current_user': request.user.username
        }
        
        return JsonResponse(response_data, status=201)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error registering patient: {str(e)}',
            'current_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'current_user': request.user.username
        }, status=500)



#  Doctor Management View
@login_required_with_message(login_url='account:login', message="You need to log in to View Doctors.", only=['management'])
def ViewDoctors(request):
    doctors = Profile.objects.filter(role='doctor').order_by('-created_at')
    # pull per_page from GET, default 10
    per_page = int(request.GET.get('per_page', 10))
    paginator = Paginator(doctors, per_page)
    page_num = request.GET.get('page')

    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # define your entries‑per‑page options here
    per_page_options = [10, 25, 50, 100]

    context = {
        'doctors': page_obj,
        'paginator': paginator,
        'per_page': per_page,
        'per_page_options': per_page_options,
    }
    return render(request, 'pages/management/view_doctors.html', context)

@login_required_with_message(login_url='account:login', message="You need to log in to View Doctors.", only=['management'])
def create_doctor(request):
    """API endpoint for creating a new doctor with profile and doctor profile"""
    try:
        # Handle form data
        email = request.POST.get('email')
        full_name = request.POST.get('full_name')
        password = request.POST.get('password')
        
        # Profile data
        phone = request.POST.get('phone', '')
        date_of_birth = request.POST.get('date_of_birth') or None
        gender = request.POST.get('gender', '')
        address = request.POST.get('address', '')
        profile_pic = request.FILES.get('profile_pic')
        
        # Notification preferences
        email_notification = request.POST.get('email_notification') == 'on'
        sms_notification = request.POST.get('sms_notification') == 'on'
        reminders = request.POST.get('reminders') == 'on'
        
        # Doctor profile data
        specialization = request.POST.get('specialization')
        qualifications = request.POST.get('qualifications', '')
        experience_years = request.POST.get('experience_years')
        license_number = request.POST.get('license_number', '')
        board_certified = request.POST.get('board_certified') == 'true'
        languages_spoken_json = request.POST.get('languages_spoken', '["English"]')
        fees = request.POST.get('fees')
        accepts_new_patients = request.POST.get('accepts_new_patients') == 'true'
        
        # Parse languages spoken
        try:
            languages_spoken = json.loads(languages_spoken_json)
        except json.JSONDecodeError:
            languages_spoken = ["English"]
        
        # Validate required fields
        if not all([email, full_name, password, specialization, experience_years, fees]):
            return JsonResponse({
                'success': False,
                'message': 'Missing required fields',
                'current_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                'current_user': request.user.username
            }, status=400)
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'message': 'Email already exists',
                'current_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                'current_user': request.user.username
            }, status=400)
        
        # Generate a unique username based on name and random characters
        current_time = datetime.now().strftime('%Y%m%d%H%M%S')  # Format: YYYYMMDDHHMMSS
        counter = str(User.objects.count() + 1).zfill(8)  # Ensure at least 6 digits
        username = f"NCMS-{current_time}-{counter}"
        
        # Create user, profile, and doctor profile in a transaction
        with transaction.atomic():
            # Create the user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=full_name  # Store full name in first_name field as per requirement
            )
            
            # Create or update the profile
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'doctor',
                    'ph_number': phone,
                    'date_of_birth': date_of_birth,
                    'gender': gender,
                    'address': address,
                    'email_notification': email_notification,
                    'sms_notification': sms_notification,
                    'reminders': reminders,
                    'is_verified': True,  # Auto-verify since created by staff
                    'is_active': True,  # Auto-activate since created by staff
                }
            )

            if not created:
                # If profile already exists, update it
                profile.role = 'doctor'
                profile.ph_number = phone
                profile.date_of_birth = date_of_birth
                profile.gender = gender
                profile.address = address   
                profile.email_notification = email_notification
                profile.sms_notification = sms_notification
                profile.reminders = reminders

                profile.is_verified = True  # Auto-verify since created by staff
                profile.is_active = True  # Auto-activate since created by staff
                profile.save()
                
            
            # Set profile picture if provided
            if profile_pic:
                profile.profile_pic = profile_pic
                profile.save()
            
            # Create doctor profile
            doctor_profile = DoctorProfile.objects.create(
                profile=profile,
                specialization=specialization,
                qualifications=qualifications,
                experience_years=int(experience_years),
                license_number=license_number,
                board_certified=board_certified,
                languages_spoken=languages_spoken,
                fees=float(fees),
                accepts_new_patients=accepts_new_patients,
                total_reviews=0
            )
            
            # Generate slug (this will be handled in the model's save method)
            doctor_profile.save()
        
        # Prepare response data
        response_data = {
            'success': True,
            'message': 'Doctor registered successfully',
            'doctor': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.first_name,
                'profile_id': profile.id,
                'doctor_profile_id': doctor_profile.id,
                'specialization': doctor_profile.specialization,
                'slug': doctor_profile.slug
            },
            'current_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'current_user': request.user.username
        }
        
        return JsonResponse(response_data, status=201)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error registering doctor: {str(e)}',
            'current_time': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'current_user': request.user.username
        }, status=500)

@login_required_with_message(login_url='account:login', message="You need to log in to update Doctor Information.", only=['management'])
def EditDoctorInfo(request):
    """
    Handle doctor information updates based on request_type
    Supports: personal, professional, fees
    """
    try:
        # Parse JSON data
        data = json.loads(request.body.decode('utf-8'))
        request_type = data.get('request_type', '').strip()
        slug = data.get('slug', '').strip()

        # Validate required fields
        if not request_type:
            return JsonResponse({
                'success': False,
                'message': 'Missing request_type parameter'
            }, status=400)
            
        if not slug:
            return JsonResponse({
                'success': False,
                'message': 'Missing slug parameter'
            }, status=400)

        # Validate request type
        valid_types = ['personal', 'professional', 'fees']
        if request_type not in valid_types:
            return JsonResponse({
                'success': False,
                'message': f'Invalid request_type. Must be one of: {", ".join(valid_types)}'
            }, status=400)

        # Get doctor profile with error handling
        try:
            doctor_profile = DoctorProfile.objects.select_related(
                'profile__user'
            ).get(slug=slug)
        except DoctorProfile.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': f'Doctor with slug "{slug}" not found'
            }, status=404)

        # Log the edit attempt

        # Process different request types
        if request_type == 'personal':
            return handle_personal_update(doctor_profile, data, request.user)
        elif request_type == 'professional':
            return handle_professional_update(doctor_profile, data, request.user)
        elif request_type == 'fees':
            return handle_fees_update(doctor_profile, data, request.user)

    except json.JSONDecodeError as e:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data provided'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An unexpected error occurred: {str(e)}'
        }, status=500)

def handle_personal_update(doctor_profile, data, user):
    """Handle personal information updates with comprehensive validation"""
    try:
        with transaction.atomic():
            profile = doctor_profile.profile
            changes_made = []

            # Update active status
            if 'active' in data:
                active = bool(data['active'])
                if profile.is_active != active:
                    profile.is_active = active
                    changes_made.append('active status')

            # Update verified status
            if 'verified' in data:
                verified = bool(data['verified'])
                if profile.is_verified != verified:
                    profile.is_verified = verified
                    changes_made.append('verified status')

            # Update phone number with validation
            if 'phone' in data:
                phone = str(data['phone']).strip()
                if phone:
                    # Remove common phone formatting characters
                    clean_phone = phone.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
                    
                    # Basic phone validation (must be digits and reasonable length)
                    if not clean_phone.isdigit() or len(clean_phone) < 7 or len(clean_phone) > 15:
                        return JsonResponse({
                            'success': False,
                            'message': 'Phone number must be 7-15 digits long and contain only numbers'
                        }, status=400)
                    
                    if profile.ph_number != phone:
                        profile.ph_number = phone
                        changes_made.append('phone number')
                else:
                    if profile.ph_number:
                        profile.ph_number = ''
                        changes_made.append('phone number (cleared)')

            # Update address
            if 'address' in data:
                address = str(data['address']).strip()
                if len(address) > 255:  # Based on model field length
                    return JsonResponse({
                        'success': False,
                        'message': 'Address cannot exceed 255 characters'
                    }, status=400)
                
                if profile.address != address:
                    profile.address = address
                    changes_made.append('address')

            # Update gender with validation
            if 'gender' in data:
                gender = str(data['gender']).strip().lower()
                valid_genders = ['male', 'female', 'other', '']
                
                if gender not in valid_genders:
                    return JsonResponse({
                        'success': False,
                        'message': 'Gender must be one of: male, female, other, or empty'
                    }, status=400)
                
                if profile.gender != gender:
                    profile.gender = gender
                    changes_made.append('gender')

            # Update date of birth with comprehensive validation
            if 'date_of_birth' in data:
                dob_str = str(data['date_of_birth']).strip()
                
                if dob_str:
                    try:
                        # Parse date string (YYYY-MM-DD format)
                        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                        
                        # Validate date is reasonable
                        current_date = date.today()
                        min_birth_year = current_date.year - 100  # Max 100 years old
                        max_birth_year = current_date.year - 18   # Min 18 years old
                        
                        if dob.year < min_birth_year:
                            return JsonResponse({
                                'success': False,
                                'message': 'Birth year cannot be more than 100 years ago'
                            }, status=400)
                        
                        if dob.year > max_birth_year or dob > current_date:
                            return JsonResponse({
                                'success': False,
                                'message': 'Doctor must be at least 18 years old'
                            }, status=400)
                        
                        if profile.date_of_birth != dob:
                            profile.date_of_birth = dob
                            changes_made.append('date of birth')
                            
                    except ValueError:
                        return JsonResponse({
                            'success': False,
                            'message': 'Invalid date format. Please use YYYY-MM-DD format'
                        }, status=400)
                else:
                    if profile.date_of_birth:
                        profile.date_of_birth = None
                        changes_made.append('date of birth (cleared)')

            

            # Save changes if any were made
            if changes_made:
                profile.save()

                send_custom_email(
                    subject='Doctor Profile Updated',
                    message=f'Dear {profile.user.first_name},\n\nYour profile has been updated successfully. Changes made: {", ".join(changes_made)}.\n\nBest regards,\nNCMS Team',
                    recipient_list=[profile.user.email],
                )
                
                return JsonResponse({
                    'success': True,
                    'message': f'Personal information updated successfully. Changes: {", ".join(changes_made)}',
                    'data': {
                        'phone': profile.ph_number,
                        'address': profile.address,
                        'gender': profile.gender,
                        'date_of_birth': profile.date_of_birth.strftime('%Y-%m-%d') if profile.date_of_birth else '',
                        'active': profile.is_active,
                        'verified': profile.is_verified,
                        'changes_made': changes_made
                    }
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': 'No changes were made to personal information',
                    'data': {
                        'phone': profile.ph_number,
                        'address': profile.address,
                        'gender': profile.gender,
                        'date_of_birth': profile.date_of_birth.strftime('%Y-%m-%d') if profile.date_of_birth else '',
                        'active': profile.active,
                        'verified': profile.verified,
                        'changes_made': []
                    }
                })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating personal information: {str(e)}'
        }, status=500)

def handle_professional_update(doctor_profile, data, user):
    """Handle professional information updates with comprehensive validation"""
    try:
        with transaction.atomic():
            changes_made = []

            # Update specialization with validation
            if 'specialization' in data:
                specialization = str(data['specialization']).strip()
                valid_specializations = [choice[0] for choice in DoctorProfile.SPECIALIZATIONS]
                
                if specialization and specialization not in valid_specializations:
                    return JsonResponse({
                        'success': False,
                        'message': f'Invalid specialization. Must be one of: {", ".join(valid_specializations)}'
                    }, status=400)
                
                if doctor_profile.specialization != specialization:
                    doctor_profile.specialization = specialization
                    changes_made.append('specialization')

            # Update qualifications
            if 'qualifications' in data:
                qualifications = str(data['qualifications']).strip()
                
                if len(qualifications) > 2000:  # Reasonable limit for text field
                    return JsonResponse({
                        'success': False,
                        'message': 'Qualifications cannot exceed 2000 characters'
                    }, status=400)
                
                if doctor_profile.qualifications != qualifications:
                    doctor_profile.qualifications = qualifications
                    changes_made.append('qualifications')

            # Update experience years with validation
            if 'experience_years' in data:
                try:
                    experience = int(data['experience_years']) if data['experience_years'] is not None else 0
                    
                    if experience < 0:
                        return JsonResponse({
                            'success': False,
                            'message': 'Experience years cannot be negative'
                        }, status=400)
                    
                    if experience > 60:
                        return JsonResponse({
                            'success': False,
                            'message': 'Experience years cannot exceed 60 years'
                        }, status=400)
                    
                    if doctor_profile.experience_years != experience:
                        doctor_profile.experience_years = experience
                        changes_made.append('experience years')
                        
                except (ValueError, TypeError):
                    return JsonResponse({
                        'success': False,
                        'message': 'Experience years must be a valid number'
                    }, status=400)

            # Update license number
            if 'license_number' in data:
                license_number = str(data['license_number']).strip()
                
                if len(license_number) > 100:  # Based on model field length
                    return JsonResponse({
                        'success': False,
                        'message': 'License number cannot exceed 100 characters'
                    }, status=400)
                
                if doctor_profile.license_number != license_number:
                    doctor_profile.license_number = license_number
                    changes_made.append('license number')

            # Update board certification
            if 'board_certified' in data:
                board_certified = bool(data['board_certified'])
                
                if doctor_profile.board_certified != board_certified:
                    doctor_profile.board_certified = board_certified
                    changes_made.append('board certification status')

            # Update languages spoken with validation
            if 'languages_spoken' in data:
                languages = data['languages_spoken']
                
                if not isinstance(languages, list):
                    return JsonResponse({
                        'success': False,
                        'message': 'Languages must be provided as a list'
                    }, status=400)
                
                # Clean and validate languages
                clean_languages = []
                for lang in languages:
                    lang_str = str(lang).strip()
                    if lang_str:
                        if len(lang_str) > 50:  # Reasonable limit per language
                            return JsonResponse({
                                'success': False,
                                'message': 'Each language name cannot exceed 50 characters'
                            }, status=400)
                        clean_languages.append(lang_str)
                
                # Remove duplicates while preserving order
                seen = set()
                unique_languages = []
                for lang in clean_languages:
                    if lang.lower() not in seen:
                        seen.add(lang.lower())
                        unique_languages.append(lang)
                
                if len(unique_languages) > 10:  # Reasonable limit
                    return JsonResponse({
                        'success': False,
                        'message': 'Cannot specify more than 10 languages'
                    }, status=400)
                
                if doctor_profile.languages_spoken != unique_languages:
                    doctor_profile.languages_spoken = unique_languages
                    changes_made.append('languages spoken')

            # Save changes if any were made
            if changes_made:
                doctor_profile.save()

                send_custom_email(
                    subject='Doctor Profile Updated',
                    message=f'Dear {doctor_profile.profile.user.first_name},\n\nYour professional information has been updated successfully.\n\nChanges made:\n- Specialization: {doctor_profile.get_specialization_display()}\n- Qualifications: {doctor_profile.qualifications}\n- Experience Years: {doctor_profile.experience_years}\n- License Number: {doctor_profile.license_number}\n- Board Certified: {"Yes" if doctor_profile.board_certified else "No"}\n- Languages Spoken: {", ".join(doctor_profile.languages_spoken)}\n\nThank you!',
                    recipient_list=[doctor_profile.profile.user.email],
                )
                
                return JsonResponse({
                    'success': True,
                    'message': f'Professional information updated successfully. Changes: {", ".join(changes_made)}',
                    'data': {
                        'specialization': doctor_profile.get_specialization_display(),
                        'specialization_code': doctor_profile.specialization,
                        'qualifications': doctor_profile.qualifications,
                        'experience_years': doctor_profile.experience_years,
                        'license_number': doctor_profile.license_number,
                        'board_certified': doctor_profile.board_certified,
                        'languages_spoken': doctor_profile.languages_spoken,
                        'changes_made': changes_made
                    }
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': 'No changes were made to professional information',
                    'data': {
                        'specialization': doctor_profile.get_specialization_display(),
                        'specialization_code': doctor_profile.specialization,
                        'qualifications': doctor_profile.qualifications,
                        'experience_years': doctor_profile.experience_years,
                        'license_number': doctor_profile.license_number,
                        'board_certified': doctor_profile.board_certified,
                        'languages_spoken': doctor_profile.languages_spoken,
                        'changes_made': []
                    }
                })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating professional information: {str(e)}'
        }, status=500)

def handle_fees_update(doctor_profile, data, user):
    """Handle fees and availability updates with comprehensive validation"""
    try:
        with transaction.atomic():
            changes_made = []

            # Update consultation fees with validation
            if 'fees' in data:
                try:
                    fees = Decimal(str(data['fees'])) if data['fees'] is not None else Decimal('0.00')
                    
                    if fees < 0:
                        return JsonResponse({
                            'success': False,
                            'message': 'Consultation fees cannot be negative'
                        }, status=400)
                    
                    # Check maximum value based on model definition (max_digits=10, decimal_places=2)
                    if fees >= Decimal('100000000.00'):  # 99,999,999.99 is the max
                        return JsonResponse({
                            'success': False,
                            'message': 'Consultation fees amount is too large (maximum: $99,999,999.99)'
                        }, status=400)
                    
                    # Validate decimal places
                    if fees.as_tuple().exponent < -2:
                        return JsonResponse({
                            'success': False,
                            'message': 'Consultation fees can have at most 2 decimal places'
                        }, status=400)
                    
                    if doctor_profile.fees != fees:
                        doctor_profile.fees = fees
                        changes_made.append('consultation fees')
                        
                except (InvalidOperation, ValueError, TypeError) as e:
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid fees amount. Please enter a valid number'
                    }, status=400)

            # Update accepts new patients status
            if 'accepts_new_patients' in data:
                accepts_new = bool(data['accepts_new_patients'])
                
                if doctor_profile.accepts_new_patients != accepts_new:
                    doctor_profile.accepts_new_patients = accepts_new
                    changes_made.append('new patient acceptance status')

            # Save changes if any were made
            if changes_made:
                doctor_profile.save()

                send_custom_email(
                    subject='Doctor Profile Updated',   
                    message=f'Dear {doctor_profile.profile.user.first_name},\n\nYour doctor profile has been updated successfully.\n\nChanges made:\n- Fees: {doctor_profile.fees}\n- Accepts New Patients: {"Yes" if doctor_profile.accepts_new_patients else "No"}\n\nThank you!',
                    recipient_list=[doctor_profile.profile.user.email],
                )
                
                return JsonResponse({
                    'success': True,
                    'message': f'Fees and availability updated successfully. Changes: {", ".join(changes_made)}',
                    'data': {
                        'fees': str(doctor_profile.fees),
                        'accepts_new_patients': doctor_profile.accepts_new_patients,
                        'changes_made': changes_made
                    }
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': 'No changes were made to fees and availability',
                    'data': {
                        'fees': str(doctor_profile.fees),
                        'accepts_new_patients': doctor_profile.accepts_new_patients,
                        'changes_made': []
                    }
                })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating fees and availability: {str(e)}'
        }, status=500)




# Medicine Management View
@login_required_with_message(login_url='account:login', message="You need to log in to View Medicines.", only=['management'])
def medicineMng(request):
    medicines = Medicine.objects.all().order_by('-created_at')

    # pull per_page from GET, default 10
    per_page = int(request.GET.get('per_page', 10))
    paginator = Paginator(medicines, per_page)
    page_num = request.GET.get('page')
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Define your entries-per-page options here
    per_page_options = [10, 25, 50, 100]

    if request.method == 'POST':
        # Handle form submission
        name = request.POST.get('name')
        generic_name = request.POST.get('generic_name')
        brand_name = request.POST.get('brand_name')
        manufacturer = request.POST.get('manufacturer')
        description = request.POST.get('description')
        default_dosage = request.POST.get('default_dosage')
        default_frequency = request.POST.get('default_frequency')
        instructions = request.POST.get('instructions')
        side_effects = request.POST.get('side_effects')

        Medicine.objects.create(
            name=name,
            generic_name=generic_name,
            brand_name=brand_name,
            manufacturer=manufacturer,
            description=description,
            default_dosage=default_dosage,
            default_frequency=default_frequency,
            instructions=instructions,
            side_effects=side_effects
        )
        messages.success(request, 'Medicine added successfully.')
        return redirect('management:medicineMng')  # Avoid resubmitting form on reload

    context = {
        'medicines': page_obj,
        'paginator': paginator,
        'per_page': per_page,
        'per_page_options': per_page_options,
    }
    return render(request, 'pages/management/medicine_management.html', context)

@login_required_with_message(login_url='account:login', message="You need to log in to Edit Medicine.", only=['management'])
def delete_medicine(request, medicine_uuid):
    try:
        medicine = Medicine.objects.get(uuid=medicine_uuid)
        medicine.delete()
        messages.success(request, 'Medicine deleted successfully.')
    except Medicine.DoesNotExist:
        messages.error(request, 'Medicine not found.')
    except ProtectedError:
        messages.error(request, 'Cannot delete this medicine as it is referenced in prescriptions.')
    except Exception as e:
        messages.error(request, 'An unexpected error occurred.')
    return redirect('management:medicineMng')




# Prescription Management View
@login_required_with_message(login_url='account:login', message="You need to log in to View Prescriptions.", only=['management'])
def precpMng(request):
    # If not POST, just display the prescriptions
    prescriptions = Prescription.objects.all().order_by('-created_at')

    # pull per_page from GET, default 10
    per_page = int(request.GET.get('per_page', 10))
    paginator = Paginator(prescriptions, per_page)
    page_num = request.GET.get('page')
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Define your entries-per-page options here
    per_page_options = [10, 25, 50, 100]

    context = {
        'prescriptions': page_obj,
        'paginator': paginator,
        'per_page': per_page,
        'per_page_options': per_page_options,
        'all_doctors': DoctorProfile.objects.all(),
        'all_medicines': Medicine.objects.all(),
        'all_patients': Profile.objects.filter(role='patient').order_by('user__first_name'),
    }
    return render(request, 'pages/management/prescription_management.html', context)

@login_required_with_message(login_url='account:login', message="You need to log in to Edit Prescription.", only=['management'])
def edit_prescription(request, prescription_uuid):
    if request.method == 'POST':
        try:
            # Parse JSON data
            prescription = Prescription.objects.get(uuid=prescription_uuid)
            data = json.loads(request.body.decode('utf-8'))

            # Update prescription details
            prescription.start_date = data.get('start_date', prescription.start_date)
            prescription.end_date = data.get('end_date', prescription.end_date)
            prescription.update_dosage = data.get('update_dosage', prescription.update_dosage)
            prescription.update_frequency = data.get('update_frequency', prescription.update_frequency)
            prescription.notes = data.get('notes', prescription.notes)
            prescription.status = data.get('status', prescription.status)

            # Update prescription schedule if provided
            if data.get('time_schedule_changed', False) and 'prescription_schedule' in data:
                prescription_schedule = data['prescription_schedule']
                if isinstance(prescription_schedule, list):
                    # Track times from the JSON data
                    json_times = {item.get('time') for item in prescription_schedule if item.get('time')}

                    # Delete schedules in the database that are not in the JSON data
                    prescription.timeschedule.exclude(time__in=json_times).delete()

                    # Iterate through the provided schedule
                    for item in prescription_schedule:
                        time = item.get('time')
                        if time:
                            # Check if a schedule with the same time exists
                            existing_schedule = prescription.timeschedule.filter(time=time).first()
                            if existing_schedule:
                                # Update the existing schedule if needed
                                had_taken = item.get('had_taken', existing_schedule.had_taken)
                                if existing_schedule.had_taken != had_taken:
                                    existing_schedule.had_taken = had_taken
                                    existing_schedule.save()
                            else:
                                # Create a new schedule if time does not match
                                prescription.timeschedule.create(time=time, had_taken=item.get('had_taken', False))
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid prescription schedule format.'
                    }, status=400)

            prescription.save()

            send_custom_email(
                subject='Prescription Updated',
                message=f'Dear {prescription.profile.user.first_name},\n\nYour prescription has been updated successfully.\n\nDetails:\n- Medicine: {prescription.medicine.name}\n- Dosage: {prescription.update_dosage}\n- Frequency: {prescription.update_frequency}\n- Notes: {prescription.notes}\n- Status: {prescription.status}\n\nThank you!',
                recipient_list=[prescription.profile.user.email],
            )

            messages.success(request, 'Prescription updated successfully.')
            return JsonResponse({
                'status': 'success',
                'message': 'Prescription updated successfully.'
            })
        except Prescription.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Prescription not found.'
            }, status=404)

        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data provided.'
            }, status=400)
        except Exception as e:
            print(f"Error updating prescription: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'An unexpected error occurred: {str(e)}'
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.'
    }, status=405)

@login_required_with_message(login_url='account:login', message="You need to log in to Add Prescription.", only=['management'])
def add_prescription(request):
    if request.method == 'POST':
        # Get form data
        patient_username = request.POST.get('patient_username')
        doctor_username = request.POST.get('doctor_username')
        medicine_uuid = request.POST.get('medicine_uuid')
        dosage = request.POST.get('update_dosage')
        frequency = request.POST.get('update_frequency')
        notes = request.POST.get('notes', '')
        status = request.POST.get('status', 'active')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # Get schedule times from the hidden input
        schedule_times_json = request.POST.get('schedule_times', '[]')
        try:
            schedule_times = json.loads(schedule_times_json)
        except json.JSONDecodeError:
            schedule_times = []
        
        # Create prescription
        try:
            # Get profile by username
            patient_profile = Profile.objects.get(user__username=patient_username)
            
            # Get doctor by username
            doctor = DoctorProfile.objects.get(profile__user__username=doctor_username)
            
            # Get medicine by UUID
            medicine = Medicine.objects.get(uuid=medicine_uuid)
            
            prescription = Prescription.objects.create(
                profile=patient_profile,
                prescribing_doctor=doctor,
                medicine=medicine,
                update_dosage=dosage,
                update_frequency=frequency,
                notes=notes,
                status=status,
                start_date=start_date,
                end_date=end_date
            )
            
            # Create schedule times
            for time_str in schedule_times:
                PrescriptionSchedule.objects.create(
                    prescription=prescription,
                    time=time_str,
                    had_taken=False
                )

            # Send email notification
            send_custom_email(
                subject='New Prescription Created',
                message=f'Dear {patient_profile.user.first_name},\n\nA new prescription has been created for you.\n\nDetails:\n- Medicine: {medicine.name}\n- Dosage: {dosage}\n- Frequency: {frequency}\n- Notes: {notes}\n- Status: {status}\n- Start Date: {start_date}\n- End Date: {end_date}\n\nThank you!',
                recipient_list=[patient_profile.user.email],
            )
            
            messages.success(request, 'Prescription created successfully!')
            # Redirect to the prescription management page
            return redirect('management:prescriptionsMng')
        except Profile.DoesNotExist:
            messages.error(request, 'Patient not found')
        except DoctorProfile.DoesNotExist:
            messages.error(request, 'Doctor not found')
        except Medicine.DoesNotExist:
            messages.error(request, 'Medicine not found')
        except Exception as e:
            # Handle errors
            messages.error(request, f'Error creating prescription: {str(e)}')
        
        return redirect('management:prescriptionsMng')
    
    # If GET request, redirect to the prescription management page
    return redirect('management:prescriptionsMng')

@login_required_with_message(login_url='account:login', message="You need to log in to Delete Prescription.", only=['management'])
def delete_prescription(request, prescription_uuid):
    try:
        prescription = Prescription.objects.get(uuid = prescription_uuid)
        prescription.delete()
        messages.success(request, 'Prescription Deleted')

    except Prescription.DoesNotExist:
        messages.error(request, 'Prescription with particulr ID not found')
    
    return redirect('management:prescriptionsMng')





# Lab Report Management View
@login_required_with_message(login_url='account:login', message="You need to log in to View Lab Reports.", only=['management'])
def labRpMng(request):
    lab_reports = LabReport.objects.all().order_by('-report_date')

    # pull per_page from GET, default 10
    per_page = int(request.GET.get('per_page', 10))
    paginator = Paginator(lab_reports, per_page)
    page_num = request.GET.get('page')
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Define your entries-per-page options here
    per_page_options = [10, 25, 50, 100]

    context = {
        'lab_reports': page_obj,
        'paginator': paginator,
        'per_page': per_page,
        'per_page_options': per_page_options,

        'all_doctors': DoctorProfile.objects.all(),
        'all_patients': Profile.objects.filter(role='patient').order_by('user__first_name'),

    }
    return render(request, 'pages/management/lab_report_management.html', context)

@require_POST
@login_required_with_message(login_url='account:login', message="You need to log in to Update Lab Report.", only=['management'])
def update_lab_report(request, labReport_uuid):
    """API endpoint for updating a lab report"""
    lab_report = get_object_or_404(LabReport, uuid=labReport_uuid)
    
    try:
        # Parse request data
        data = json.loads(request.body)
        
        # Update lab report fields
        lab_report.report_type = data.get('report_type', lab_report.report_type)
        lab_report.report_date = data.get('report_date', lab_report.report_date)
        lab_report.status = data.get('status', lab_report.status)
        lab_report.report_description = data.get('report_description', lab_report.report_description)
        lab_report.save()
        
        send_custom_email(
            subject='Lab Report Updated',   
            message=f'Dear {lab_report.patient_profile.user.first_name},\n\nYour lab report has been updated successfully.\n\nDetails:\n- Report Type: {lab_report.report_type}\n- Report Date: {lab_report.report_date}\n- Status: {lab_report.status}\n- Description: {lab_report.report_description}\n\nThank you!',
            recipient_list=[lab_report.patient_profile.user.email],
        )

        # Handle parameters
        if 'parameters' in data:
            # Delete existing parameters
            lab_report.parameters.all().delete()
            
            # Create new parameters
            for param_data in data['parameters']:
                LabReportParameter.objects.create(
                    lab_report=lab_report,
                    parameter_name=param_data['parameter_name'],
                    result=param_data['result'],
                    reference_range=param_data['reference_range'],
                    status=param_data['status']
                )
        
        # Prepare response data
        response_data = {
            'uuid': str(lab_report.uuid),
            'report_type': lab_report.report_type,
            'report_date': lab_report.report_date.isoformat() if hasattr(lab_report.report_date, 'isoformat') else str(lab_report.report_date),
            'status': lab_report.status,
            'doctor_name': lab_report.doctor.profile.user.first_name,
            'doctor_username': lab_report.doctor.profile.user.username,
            'patient_name': lab_report.patient_profile.user.first_name,
            'patient_username': lab_report.patient_profile.user.username,
            'report_description': lab_report.report_description,
            'created_at': lab_report.created_at.isoformat(),
            'updated_at': lab_report.updated_at.isoformat(),
            'parameters': [
                {
                    'parameter_name': param.parameter_name,
                    'result': param.result,
                    'reference_range': param.reference_range,
                    'status': param.status
                }
                for param in lab_report.parameters.all()
            ]
        }
        
        return JsonResponse(response_data)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_POST
@login_required_with_message(login_url='account:login', message="You need to log in to Create Lab Report.", only=['management'])
def create_lab_report(request):
    """View for creating a new lab report from JSON data"""
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        
        # Get required data from the JSON
        patient_username = data.get('patient_username')
        doctor_username = data.get('doctor_username')
        report_type = data.get('report_type')
        report_date = data.get('report_date')
        status = data.get('status')
        report_description = data.get('report_description')
        parameters = data.get('parameters', [])
        
        # Validate required fields
        if not all([patient_username, doctor_username, report_type, report_date, status]):
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required fields'
            }, status=400)
        
        # Create lab report
        patient_profile = Profile.objects.get(user__username=patient_username)
        doctor = DoctorProfile.objects.get(profile__user__username=doctor_username)
        
        lab_report = LabReport.objects.create(
            patient_profile=patient_profile,
            doctor=doctor,
            report_type=report_type,
            report_date=report_date,
            status=status,
            report_description=report_description
        )
        
        # Create parameters
        for param_data in parameters:
            LabReportParameter.objects.create(
                lab_report=lab_report,
                parameter_name=param_data['parameter_name'],
                result=param_data['result'],
                reference_range=param_data['reference_range'],
                status=param_data['status']
            )

        # Send email notification
        send_custom_email(
            subject='Lab Report Created',
            message=f'Dear {patient_profile.user.first_name},\n\nA new lab report has been created for you.\n\nDetails:\n- Report Type: {report_type}\n- Report Date: {report_date}\n- Status: {status}\n- Description: {report_description}\n\nThank you!',
            recipient_list=[patient_profile.user.email],
        )

        messages.success(request, 'Lab report created successfully.')
        return JsonResponse({
            'status': 'success',
            'message': 'Lab report created successfully',
            'uuid': str(lab_report.uuid)
        })
    
    except Profile.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Patient not found'
        }, status=404)
    except DoctorProfile.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Doctor not found'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error creating lab report: {str(e)}'
        }, status=500)

@login_required_with_message(login_url='account:login', message="You need to log in to Delete Lab Report.", only=['management'])
def delete_lab_report(request, labReport_uuid):
    """View for deleting a lab report"""
    lab_report = get_object_or_404(LabReport, uuid=labReport_uuid)
    lab_report.delete()
    # Add a success message here if you're using Django messages framework
    messages.success(request, 'Lab report deleted successfully.')
    return redirect('management:labreportMng')

