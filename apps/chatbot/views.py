"""
API views for the CourseCart chatbot.
"""
import json
import traceback
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .services import ChatbotService

@csrf_exempt
@require_POST
def chat_api(request):
    """
    Main chatbot endpoint with thinking simulation.
    
    POST /chatbot/api/chat/
    Body: {"message": "your question"}
    
    Returns thinking steps + response.
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({
                'response': 'Please ask me a question! I\'m here to help with courses, payments, our team, or anything about CourseCart! 😊',
                'thinking_steps': [],
                'intent': 'greeting',
                'error': None
            })
        
        if len(user_message) > 500:
            return JsonResponse({
                'response': 'Could you keep it a bit shorter? I want to give you the best answer! 😊',
                'thinking_steps': [],
                'intent': 'general',
                'error': None
            })
        
        # User context
        user_name = request.user.full_name if request.user.is_authenticated else 'Student'
        user_role = 'student' if (request.user.is_authenticated and request.user.is_student) else \
                    'instructor' if (request.user.is_authenticated and request.user.is_instructor) else 'anonymous'
        
        # Get smart response
        result = ChatbotService.get_smart_response(user_message, user_name, user_role)
        
        return JsonResponse({
            'response': result['response'],
            'thinking_steps': result['thinking_steps'],
            'intent': result['intent'],
            'confidence': result['confidence'],
            'strategy': result['strategy'],
            'interaction_id': result.get('interaction_id'),
            'error': None
        })
        
    except Exception as e:
        print(f"Chatbot Error: {traceback.format_exc()}")
        return JsonResponse({
            'response': 'I need a moment to think. Please try again! 🙏',
            'thinking_steps': [],
            'error': str(e)
        }, status=500)


def suggested_questions(request):
    """Smart suggested questions."""
    return JsonResponse({
        'questions': [
            {"text": "📚 What courses are available?", "icon": "📚"},
            {"text": "💰 How do I pay for a course?", "icon": "💰"},
            {"text": "👥 Who built CourseCart?", "icon": "👥"},
            {"text": "🎓 How do I get a certificate?", "icon": "🎓"},
            {"text": "👨‍🏫 How can I become an instructor?", "icon": "👨‍🏫"},
            {"text": "🏢 Tell me about CourseCart", "icon": "🏢"},
        ]
    })

def health_check(request):
    """Health check endpoint."""
    return JsonResponse({
        'status': 'ok',
        'message': 'CourseCart Chatbot is operational',
        'intents': len(ChatbotService.RESPONSES)
    })