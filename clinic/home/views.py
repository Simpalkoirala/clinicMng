from django.shortcuts import render

from django.contrib import messages


# Create your views here.


def home_page(request):
    return render(request, 'pages/index.html')

def home_page2(request):
    return render(request, 'others/index1.html')


def BookAppoinment(request):
    return render(request, 'pages/patient/book_appoinment.html')

def ViewDocument(request):
    return render(request, 'pages/patient/view_document.html')


def message(request):
    return render(request, 'pages/patient/message.html')


def labReport(request):
    return render(request, 'pages/patient/lab_report.html')


def prescriptions(request):
    return render(request, 'pages/patient/prescriptions.html')


def login(request):
    return render(request, 'pages/login.html')

def register(request):
    return render(request, 'pages/register.html')


def patientDashboardOld(request):
    return render(request, 'others/patient_dashboard.html')


def patientDashboard(request):
    return render(request, 'pages/patient/dashboard.html')


def viewAppoinment(request):
    return render(request, 'pages/patient/view_appoinment.html')
















def doctor(request):
    return render(request, 'pages/doctor/dashboard.html')


def d_edit_schedules(request):
    return render(request, 'pages/doctor/edit_schedules.html')