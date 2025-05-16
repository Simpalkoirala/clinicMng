from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django import forms
from doctor.models import DoctorProfile
from account.models import Profile
# Create your views here.


def home_page(request):
    all_doc_profiles = DoctorProfile.objects.all()



    return render(request, 'pages/index.html', {'all_doc_profiles': all_doc_profiles})





def home_page2(request):
    return render(request, 'others/index1.html')



def patientDashboardOld(request):
    return render(request, 'others/patient_dashboard.html')




def terms(request):
    return render(request, 'pages/index.html')







def ViewPatients(request):
    return render(request, 'pages/doctor/view_patients.html')



def management(request):
    return render(request, 'pages/management/dashboard.html')








class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = [
            'specialization',
            'qualifications',
            'experience_years',
            'license_number',
            'board_certified',
            'languages_spoken',
            'fees',
            'accepts_new_patients',
        ]
        widgets = {
            'languages_spoken': forms.TextInput(attrs={
                'placeholder': 'e.g. ["English", "Nepali"]'
            }),
        }



def create_doctor_profile(request):
    # Ensure the user is a doctor
    profile = getattr(request.user, 'profile', None)

    

    if request.method == 'POST':
        form = DoctorProfileForm(request.POST)
        if form.is_valid():
            doctor_profile = form.save(commit=False)
            return redirect('doctor_profile_detail', slug=doctor_profile.slug)
    else:
        form = DoctorProfileForm()

    return render(request, 'pages/management/d-profile_create.html', {'form': form, 'action': 'Create'})

def update_doctor_profile(request, slug):
    profile = getattr(request.user, 'profile', None)

    doctor_profile = get_object_or_404(DoctorProfile, slug=slug)


    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, instance=doctor_profile)
        if form.is_valid():
            form.save()
            return redirect('doctor_profile_detail', slug=doctor_profile.slug)
    else:
        form = DoctorProfileForm(instance=doctor_profile)

    return render(request, 'pages/management/d-profile_create.html', {'form': form, 'action': 'Update'})