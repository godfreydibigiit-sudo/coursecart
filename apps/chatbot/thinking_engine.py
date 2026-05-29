"""
Thinking engine that simulates AI reasoning before answering.
Shows realistic thinking steps to the user.
"""
import random
import time
from datetime import datetime


class ThinkingEngine:
    """
    Simulates an AI thinking process for realistic UX.
    Shows step-by-step reasoning messages before the final answer.
    """
    
    @staticmethod
    def get_thinking_sequence(intent, message, context=None):
        """
        Generate a sequence of thinking steps based on intent.
        
        Returns:
            list of dicts: [{'message': str, 'duration': int}, ...]
        """
        sequences = {
            'courses': [
                {'message': '🔍 Analyzing your course preferences...', 'duration': 600},
                {'message': '📚 Searching our course catalog...', 'duration': 800},
                {'message': '✅ Found matching courses!', 'duration': 400},
            ],
            'payments': [
                {'message': '💳 Checking available payment methods...', 'duration': 500},
                {'message': '💰 Verifying pricing information...', 'duration': 700},
                {'message': '🔒 Confirming secure payment options...', 'duration': 400},
            ],
            'enrollment': [
                {'message': '📝 Preparing enrollment guide...', 'duration': 500},
                {'message': '✅ Checking course availability...', 'duration': 600},
                {'message': '🎓 Ready with enrollment steps!', 'duration': 400},
            ],
            'certificates': [
                {'message': '📜 Looking up certification policy...', 'duration': 500},
                {'message': '🏆 Checking completion requirements...', 'duration': 600},
                {'message': '🎖️ Certificate information ready!', 'duration': 400},
            ],
            'instructor': [
                {'message': '👨‍🏫 Preparing instructor guidelines...', 'duration': 500},
                {'message': '📚 Checking course creation requirements...', 'duration': 600},
                {'message': '💡 Instructor information ready!', 'duration': 400},
            ],
            'platform_help': [
                {'message': '🗺️ Navigating the platform...', 'duration': 500},
                {'message': '📍 Finding the right feature...', 'duration': 600},
                {'message': '✅ Help information ready!', 'duration': 400},
            ],
            'general': [
                {'message': '🤔 Analyzing your question...', 'duration': 600},
                {'message': '💭 Processing the best response...', 'duration': 700},
                {'message': '✨ Answer ready!', 'duration': 400},
            ],
        }
        
        return sequences.get(intent, sequences['general'])
    
    @staticmethod
    def simulate_thinking(intent):
        """
        Simulate brief thinking delay for realism.
        Returns after a short random duration.
        """
        base_delay = {
            'courses': 1.0,
            'payments': 0.8,
            'enrollment': 0.9,
            'certificates': 0.7,
            'instructor': 0.9,
            'platform_help': 0.8,
            'general': 1.0,
        }
        
        delay = base_delay.get(intent, 1.0) + random.uniform(0, 0.5)
        time.sleep(min(delay, 1.5))  # Cap at 1.5 seconds
    
    @staticmethod
    def get_confidence_display(confidence):
        """Get a human-readable confidence display."""
        if confidence > 0.8:
            return 'High confidence'
        elif confidence > 0.5:
            return 'Moderate confidence'
        else:
            return 'Learning from this question...'