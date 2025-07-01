from django.shortcuts import render

def index(request):
    return render(request, 'index.html')
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyBegFihxe47BeSumPIh4Qa_6UWl_VT69VQ')

@csrf_exempt
def ask_ai(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('question', '')

        if not question and data.get("planet_name"):
            question = f"Tell me a brief, interesting fact about the planet {data['planet_name']}."

        response = requests.post(
            'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent',
            params={'key': GEMINI_API_KEY},
            json={"contents": [{"parts": [{"text": question}]}]},
            headers={"Content-Type": "application/json"}
        )

        result = response.json()
        try:
            parts = result.get("candidates", [])[0]["content"]["parts"]
            return JsonResponse({"answer": parts[0]["text"]})
        except Exception as e:
            print("Gemini Error:", e)
            return JsonResponse({"answer": "No response from Gemini."})
