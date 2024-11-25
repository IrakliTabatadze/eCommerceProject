from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('registration/', views.RegistrationUserView.as_view(), name='registration'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout/', views.LogoutUserView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]
