from django.urls import path
from .views import chat_response, get_weather

urlpatterns = [
    path('konnection/', chat_response, name='chat_response'),
    path('weather/', get_weather, name='get_weather'),
]