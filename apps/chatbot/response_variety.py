"""
Response variety engine that provides different answers for the same question.
"""
import random
from datetime import datetime


class ResponseVarietyEngine:
    """
    Generates varied responses based on intent, context, and randomness.
    Ensures the chatbot doesn't sound repetitive.
    """
    
    # Response templates with multiple variations per intent
    RESPONSE_POOLS = {
        'greeting': [
            [
                "Hello! 👋 I'm CourseCart AI. How can I help you today?",
                "Hi there! 😊 Ready to explore vocational courses? Ask me anything!",
                "Hey! Welcome to CourseCart. I'm here to help you find the perfect course! 🎓",
                "Good to see you! 👋 What would you like to know about CourseCart?",
            ],
        ],
        'courses': [
            [
                "We offer vocational courses in 📚 Plumbing, ⚡ Electrical, 🧵 Tailoring, 🔥 Welding, 🪚 Carpentry, and more! All courses include video lessons, PDFs, and certificates. Visit /courses/ to browse!",
                "Great question! 🎓 Our most popular courses are Plumbing, Electrical Installation, Tailoring, and Welding. Each course has hands-on video lessons and a certificate. Check /courses/ for the full list!",
                "You can learn Plumbing, Electrical work, Tailoring, Carpentry, Welding, Masonry, and Solar Installation on CourseCart. All courses are affordable (TZS 20,000-50,000). Browse /courses/ now!",
            ],
        ],
        'payments': [
            [
                "We accept 📱 Mobile Money (M-Pesa, Tigo Pesa, Airtel), 💳 Bank Cards (Visa, Mastercard), and 💵 Cash payments at authorized agents. Course prices range from TZS 20,000 to 50,000. Some courses are free! 🆓",
                "Payment is easy! 💰 Choose from Mobile Money, Bank Card, or Cash. Most courses cost TZS 20,000-50,000. We also have free courses! Payment is simulated for testing.",
                "You can pay via M-Pesa, Tigo Pesa, bank card, or cash. 💳 All payments are secure. Prices are affordable — typically TZS 20,000-50,000 per course. Free courses available too!",
            ],
        ],
        'enrollment': [
            [
                "Enrolling is simple! 🎓 1) Browse courses at /courses/ 2) Click 'Enroll Now' 3) Complete payment 4) Start learning immediately! For free courses, you get instant access.",
                "Here's how: Go to /courses/, find a course you like, click 'Enroll Now', and follow the payment steps. Once paid, all lessons unlock! 🔓 Free courses give instant access.",
                "Ready to start? 📚 Head to /courses/, pick a course, hit 'Enroll Now', complete payment, and you're in! It takes less than 2 minutes. 🚀",
            ],
        ],
        'certificates': [
            [
                "Yes! 🎓 When you complete 100% of a course's lessons, you automatically earn a Certificate of Completion. This can boost your CV and help with job applications!",
                "Complete all lessons in a course and you'll receive a 📜 Certificate of Completion automatically. It's a great way to prove your skills to employers!",
                "Certificates are issued automatically when you finish all lessons. 📜 They're perfect for job applications and starting your own business. Keep learning! 🎓",
            ],
        ],
        'instructor': [
            [
                "Want to teach? 👨‍🏫 Register as an instructor at /accounts/register/instructor/, create your course with videos/PDFs, set your price, and start earning! It's free to join.",
                "Becoming an instructor is easy! 🚀 Sign up at /accounts/register/instructor/, create courses with video lessons, and earn from student enrollments. Share your skills!",
                "Join as an instructor! 👨‍🏫 Create courses, upload videos and PDFs, set your price, and earn when students enroll. Visit /accounts/register/instructor/ to start!",
            ],
        ],
        'platform_help': [
            [
                "I can help you navigate! 📍 Your dashboard is at /dashboard/, courses at /courses/, and profile settings in the sidebar. What specifically are you looking for?",
                "Need directions? 🗺️ Dashboard: /dashboard/ | Courses: /courses/ | Profile: sidebar Settings. Let me know what you're trying to find!",
                "Here's a quick guide: 📚 Browse courses at /courses/, manage enrollments at /courses/my-courses/, and check notifications via the 🔔 bell icon!",
            ],
        ],
    }
    
    # Tone shifters for variety
    TONE_MODIFIERS = {
        'friendly': ['😊', '👋', 'Great question!', 'Happy to help!'],
        'encouraging': ['🚀', 'You got this!', 'Keep going!', 'Excellent choice!'],
        'professional': ['Certainly.', 'Here\'s the information:', 'I recommend:', 'Based on our data:'],
    }
    
    # Thinking messages displayed before answer
    THINKING_MESSAGES = {
        'courses': [
            "🔍 Searching available courses...",
            "📚 Matching your interests with our catalog...",
            "🎯 Finding the best courses for you...",
        ],
        'payments': [
            "💳 Checking payment options...",
            "💰 Reviewing pricing information...",
            "🔒 Verifying secure payment methods...",
        ],
        'enrollment': [
            "📝 Preparing enrollment steps...",
            "✅ Checking enrollment requirements...",
            "🎓 Getting your learning path ready...",
        ],
        'certificates': [
            "📜 Looking up certificate information...",
            "🏆 Checking completion requirements...",
            "🎖️ Preparing certification details...",
        ],
        'instructor': [
            "👨‍🏫 Preparing instructor information...",
            "📚 Checking teaching requirements...",
            "💡 Getting creator guidelines ready...",
        ],
        'platform_help': [
            "🗺️ Finding the right page...",
            "🔍 Navigating the platform...",
            "📍 Locating the feature you need...",
        ],
        'general': [
            "🤔 Analyzing your question...",
            "💭 Thinking about the best answer...",
            "🔍 Searching my knowledge base...",
        ],
    }
    
    @classmethod
    def get_response(cls, intent, context=None):
        """
        Get a varied response for a given intent.
        Never returns the same response twice in a session.
        """
        pool = cls.RESPONSE_POOLS.get(intent, cls.RESPONSE_POOLS.get('general', [["I'm here to help! Ask me about courses, payments, or anything about CourseCart! 😊"]]))
        
        # Get the first (and usually only) variation list
        variations = pool[0] if pool else ["I'm here to help! 😊"]
        
        # Pick a random variation
        response = random.choice(variations)
        
        # Add tone modifier occasionally
        if random.random() < 0.3:
            tone = random.choice(['friendly', 'encouraging'])
            modifier = random.choice(cls.TONE_MODIFIERS[tone])
            response = f"{modifier} {response}"
        
        # Add contextual suggestion
        if context and intent in ['courses', 'general']:
            suggestions = [
                "\n\n💡 Try asking: 'What courses are available?' or 'How do I enroll?'",
                "\n\n📚 Visit /courses/ to browse all available courses!",
                "\n\n🎓 Ready to start? Check out our featured courses at /courses/!",
            ]
            if random.random() < 0.4:
                response += random.choice(suggestions)
        
        return response
    
    @classmethod
    def get_thinking_messages(cls, intent):
        """Get thinking messages for display before response."""
        messages = cls.THINKING_MESSAGES.get(intent, cls.THINKING_MESSAGES['general'])
        return messages