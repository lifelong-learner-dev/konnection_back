from django.shortcuts import render
from django.http import JsonResponse
import google.generativeai as genai
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import requests, datetime

genai.configure(api_key=settings.GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

@csrf_exempt
def chat_response(request):
    if request.method == "POST":
        message = request.POST.get("message")
        if message:
            response = chat.send_message(message)
            return JsonResponse({"response": response.text})
    return JsonResponse({"error": "Invalid request"}, status=400)


OPENWEATHER_API_KEY = settings.OPENWEATHER_API_KEY

@csrf_exempt
def get_weather(request):
    if request.method == 'POST':
        action = request.POST.get('action', '').lower()
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        if latitude and longitude:
            if action == '오늘 날씨':
                weather_data = fetch_today_weather(latitude, longitude)
            elif action == '이번주 날씨':
                weather_data = fetch_week_weather(latitude, longitude)
            else:
                return JsonResponse({'error': 'Invalid action'}, status=400)

            return JsonResponse(weather_data)
        else:
            return JsonResponse({'error': 'Invalid location data'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def fetch_today_weather(latitude, longitude):
    url = f"http://api.openweathermap.org/data/2.5/onecall?lat={latitude}&lon={longitude}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    
    # 오늘의 날씨 정보 추출
    min_temp = data['daily'][0]['temp']['min']
    max_temp = data['daily'][0]['temp']['max']
    weather_description = data['current']['weather'][0]['description']
    
    # 오늘 강수 여부 확인
    rain_info = ''
    if 'rain' in data['hourly'][0]:
        rain_info = f"비가 {data['hourly'][0]['rain']} mm 올 예정입니다."

    return {
        'min_temp': min_temp,
        'max_temp': max_temp,
        'weather_description': weather_description,
        'rain_info': rain_info
    }

def fetch_week_weather(latitude, longitude):
    url = f"http://api.openweathermap.org/data/2.5/onecall?lat={latitude}&lon={longitude}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    
    # 이번 주 강수 예보 확인
    rain_days = [
        {
            'date': day['dt'],
            'description': day['weather'][0]['description']
        }
        for day in data['daily'] if 'rain' in day['weather'][0]['description'].lower()
    ]

    rain_dates = [
        {'date': datetime.datetime.fromtimestamp(day['date']).strftime('%Y-%m-%d'), 'description': day['description']}
        for day in rain_days
    ]

    return {
        'rain_dates': rain_dates
    }
