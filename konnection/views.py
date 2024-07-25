from django.shortcuts import render
from django.http import JsonResponse
import google.generativeai as genai
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

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
