from django.shortcuts import render

# Create your views here.

def doctorDashboard(request):
    return render(request, 'pages/doctor/dashboard.html')


def d_edit_schedules(request):
    return render(request, 'pages/doctor/edit_schedules.html')


def ViewPatients(request):
    return render(request, 'pages/doctor/view_patients.html')


def OnlineSession(request):
    return render(request, 'pages/doctor/online_session.html')


def dSetting(request):
    return render(request, 'pages/doctor/setting.html')


def d_profile(request):
    return render(request, 'pages/doctor/profile.html')
