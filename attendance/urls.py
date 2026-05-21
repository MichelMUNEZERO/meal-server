from django.urls import path

from attendance import views


urlpatterns = [
    path('attendance/', views.attendance_list),
    path('attendance/qr/', views.generate_qr),
    path('attendance/verify/', views.verify_scan),
]
