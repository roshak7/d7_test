from django.urls import path
from .views import *



urlpatterns = [
    path('make_appointment/', AppointmentView.as_view(), name='make_appointment'),
]