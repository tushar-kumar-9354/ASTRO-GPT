from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
import requests
import logging

# Set up logging
logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html')

@csrf_exempt
def ask_ai(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Get API key from environment
        GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY not configured")
            return JsonResponse({"answer": "Service configuration error"}, status=500)

        # Parse request data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        question = data.get('question', '')
        planet_name = data.get('planet_name', '')

        # Generate default question if needed
        if not question and planet_name:
            question = f"Tell me a brief, interesting fact about the planet {planet_name}."
        elif not question:
            return JsonResponse({'error': 'No question provided'}, status=400)

        # Call Gemini API
        response = requests.post(
            'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent',
            params={'key': GEMINI_API_KEY},
            json={
                "contents": [{
                    "parts": [{"text": question}]
                }],
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_ONLY_HIGH"
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": 800,
                    "temperature": 0.9,
                    "topP": 1
                }
            },
            headers={"Content-Type": "application/json"},
            timeout=10  # Add timeout
        )

        response.raise_for_status()  # Raises exception for 4XX/5XX responses
        
        # Parse response
        result = response.json()
        try:
            parts = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])
            if parts and "text" in parts[0]:
                return JsonResponse({"answer": parts[0]["text"]})
            return JsonResponse({"answer": "No valid response from Gemini."})
            
        except (KeyError, IndexError) as e:
            logger.error(f"Gemini response parsing error: {e}\nFull response: {result}")
            return JsonResponse({"answer": "Error processing Gemini response."})

    except requests.exceptions.RequestException as e:
        logger.error(f"Gemini API request failed: {e}")
        return JsonResponse({"answer": "Failed to connect to Gemini service."}, status=502)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JsonResponse({"answer": "An unexpected error occurred."}, status=500)