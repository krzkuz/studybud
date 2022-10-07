from unicodedata import name
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/<str:pk>/', views.profile, name='profile'),
    path('room/<str:pk>/', views.room, name='room'),
    path('create/', views.create_room, name='create_room'),
    path('update/<str:pk>', views.update_room, name='update_room'),
    path('delete/<str:pk>', views.delete_room, name='delete_room'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('register/', views.register, name='register'),
    path('delete-message/<str:pk>/<int:key>', views.delete_message, name='delete_message'),
    path('settings', views.settings, name='settings'),
    path('topics', views.topics_mobile, name='topics_mobile'),
    path('activity', views.activity_mobile, name='activity_mobile'),
]