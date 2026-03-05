from django.urls import path
from . import views

app_name = 'insurance'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('plans/', views.plan_list, name='plan_list'),
    path('plans/<int:pk>/', views.plan_detail, name='plan_detail'),
    path('calculator/', views.premium_calculator, name='premium_calculator'),
    path('claims/', views.claim_list, name='claim_list'),
    path('claims/new/', views.claim_create, name='claim_create'),
    path('claims/<int:pk>/', views.claim_detail, name='claim_detail'),
    path('profiles/', views.user_profile_list, name='user_profile_list'),
    path('profiles/new/', views.user_profile_create, name='user_profile_create'),
    path('profiles/<int:pk>/edit/', views.user_profile_edit, name='user_profile_edit'),
]
