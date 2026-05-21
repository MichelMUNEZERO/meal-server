from django.urls import path

from meals import views


urlpatterns = [
    path('users/<int:user_id>/meal-plan/', views.user_meal_plan),
    path('meal-plans/', views.all_meal_plans),
]
