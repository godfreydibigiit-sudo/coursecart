"""
Intent classification using keyword matching and pattern recognition.
"""
import re
from collections import Counter


class IntentClassifier:
    """
    Classifies user messages into intent categories.
    Uses multi-layer keyword matching with confidence scoring.
    """
    
    # Intent patterns with weighted keywords
    INTENT_PATTERNS = {
        'courses': {
            'keywords': [
                'course', 'courses', 'available', 'offer', 'learn', 'study',
                'training', 'skill', 'skills', 'class', 'classes', 'program',
                'plumbing', 'electrical', 'tailoring', 'welding', 'carpentry',
                'category', 'categories', 'what do you', 'what can i'
            ],
            'weight': 1.0
        },
        'enrollment': {
            'keywords': [
                'enroll', 'enrollment', 'join', 'register', 'sign up',
                'start', 'begin', 'take course', 'get started', 'how do i'
            ],
            'weight': 1.0
        },
        'payments': {
            'keywords': [
                'pay', 'payment', 'price', 'cost', 'fee', 'amount',
                'mpesa', 'tigo', 'airtel', 'mobile money', 'bank',
                'card', 'cash', 'pay for', 'how much', 'tzs', 'free'
            ],
            'weight': 1.0
        },
        'certificates': {
            'keywords': [
                'certificate', 'certification', 'certified', 'completion',
                'credential', 'qualification', 'proof', 'document'
            ],
            'weight': 1.0
        },
        'instructor': {
            'keywords': [
                'teach', 'teaching', 'instructor', 'create course',
                'become', 'upload', 'publish', 'earn money'
            ],
            'weight': 1.0
        },
        'platform_help': {
            'keywords': [
                'how to', 'where', 'find', 'navigate', 'dashboard',
                'profile', 'settings', 'account', 'login', 'password',
                'help', 'support', 'contact', 'issue', 'problem'
            ],
            'weight': 0.8
        },
        'greeting': {
            'keywords': [
                'hello', 'hi', 'hey', 'good morning', 'good afternoon',
                'good evening', 'how are you', 'what\'s up', 'greetings'
            ],
            'weight': 0.5
        }
    }
    
    @classmethod
    def classify(cls, message):
        """
        Classify a user message and return the intent with confidence.
        
        Returns:
            dict: {'intent': str, 'confidence': float, 'keywords_matched': list}
        """
        message_lower = message.lower().strip()
        scores = {}
        matched_keywords = {}
        
        for intent, pattern in cls.INTENT_PATTERNS.items():
            score = 0
            matched = []
            
            for keyword in pattern['keywords']:
                if keyword in message_lower:
                    score += 1
                    matched.append(keyword)
            
            # Weight the score
            weighted_score = (score / max(len(pattern['keywords']), 1)) * pattern['weight']
            scores[intent] = weighted_score
            matched_keywords[intent] = matched
        
        # Find the best intent
        if scores:
            best_intent = max(scores, key=scores.get)
            confidence = scores[best_intent]
            
            # If confidence is too low, default to general
            if confidence < 0.1:
                return {
                    'intent': 'general',
                    'confidence': 0.3,
                    'keywords_matched': []
                }
            
            return {
                'intent': best_intent,
                'confidence': min(confidence, 1.0),
                'keywords_matched': matched_keywords[best_intent]
            }
        
        return {
            'intent': 'general',
            'confidence': 0.1,
            'keywords_matched': []
        }
    
    @classmethod
    def get_all_intents(cls):
        """Return list of all supported intents."""
        return list(cls.INTENT_PATTERNS.keys())