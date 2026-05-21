from django.urls import path

from users import views


urlpatterns = [
    path('auth/login/', views.login_view),
    path('auth/logout/', views.logout_view),
    path('auth/password-reset/', views.password_reset_request),
    path('auth/password-reset/confirm/', views.password_reset_confirm),
    path('auth/change-password/', views.change_password),
    path('session', views.session_view),
    path('session/', views.session_view),
    path('users/', views.users_list),
    path('users/create/', views.create_user),
    path('users/bulk-import/', views.bulk_import_users),
    path('users/<int:user_id>/', views.user_detail),
    path('users/<int:user_id>/send-password-reset/', views.send_password_reset),
]
