"""
CourseCart AI Chatbot Service - Professional Edition
Multi-strategy AI with thinking simulation, team awareness, and brand personality.
"""
import os
import json
import hashlib
import random
import time
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone


class ChatbotService:
    """
    CourseCart AI Assistant - Professional Chatbot Service.
    Knows about the platform, the development team, and uses brand personality.
    """
    
    # ============================================================
    # BRAND IDENTITY
    # ============================================================
    BRAND = {
        'name': 'CourseCart',
        'tagline': 'Online Vocational Skills Training Platform',
        'website': 'coursecart.pythonanywhere.com',
        'logo_emoji': '📚',
        'colors': 'Teal (#0D9488) and Warm Amber (#F59E0B)',
    }
    
    # ============================================================
    # DEVELOPMENT TEAM
    # ============================================================
    TEAM = {
        'project_manager': {
            'name': 'Neema Manoza',
            'role': 'Project Manager',
            'emoji': '📋',
            'expertise': 'Project planning, timeline management, quality assurance, stakeholder coordination',
        },
        'backend_developer': {
            'name': 'Godfrey Augustino',
            'role': 'Backend Developer',
            'emoji': '💻',
            'expertise': 'Django architecture, database design, API logic, payment simulation, authentication systems',
        },
        'frontend_developer': {
            'name': 'Modesti Imam',
            'role': 'Frontend Developer',
            'emoji': '🎨',
            'expertise': 'Responsive HTML/CSS, JavaScript interactions, UI components, cross-browser compatibility',
        },
        'uiux_designer': {
            'name': 'Mustapha Lameck',
            'role': 'UI/UX Designer',
            'emoji': '🖌️',
            'expertise': 'Visual design systems, wireframes, prototypes, user experience, color schemes',
        },
        'business_analyst': {
            'name': 'Doreen Aloyce',
            'role': 'Business Analyst',
            'emoji': '📊',
            'expertise': 'Market research, business requirements, use cases, functional specifications',
        },
    }
    
    # ============================================================
    # THINKING ENGINE - Realistic AI reasoning simulation
    # ============================================================
    THINKING_SEQUENCES = {
        'greeting': [
            {"message": "👋 Recognizing user presence...", "duration": 400},
            {"message": "✨ Preparing warm welcome...", "duration": 500},
        ],
        'courses': [
            {"message": "🔍 Analyzing course preferences...", "duration": 600},
            {"message": "📚 Searching CourseCart catalog...", "duration": 800},
            {"message": "🎯 Matching best courses for you...", "duration": 500},
        ],
        'payments': [
            {"message": "💳 Identifying payment methods...", "duration": 500},
            {"message": "💰 Checking pricing database...", "duration": 600},
            {"message": "🔒 Verifying secure payment options...", "duration": 400},
        ],
        'enrollment': [
            {"message": "📝 Preparing enrollment workflow...", "duration": 500},
            {"message": "✅ Checking course availability...", "duration": 600},
            {"message": "🎓 Ready with step-by-step guide...", "duration": 400},
        ],
        'certificates': [
            {"message": "📜 Accessing certification policy...", "duration": 500},
            {"message": "🏆 Checking completion criteria...", "duration": 600},
        ],
        'instructor': [
            {"message": "👨‍🏫 Loading instructor guidelines...", "duration": 500},
            {"message": "📚 Preparing creator resources...", "duration": 600},
            {"message": "💡 Instructor pathway ready...", "duration": 400},
        ],
        'team': [
            {"message": "👥 Accessing team database...", "duration": 500},
            {"message": "📋 Retrieving team member details...", "duration": 600},
            {"message": "✅ Team information ready...", "duration": 400},
        ],
        'platform_help': [
            {"message": "🗺️ Navigating CourseCart platform...", "duration": 500},
            {"message": "📍 Locating requested feature...", "duration": 600},
        ],
        'about': [
            {"message": "📚 Loading CourseCart information...", "duration": 500},
            {"message": "🏢 Retrieving platform details...", "duration": 600},
            {"message": "✨ Brand story ready...", "duration": 400},
        ],
        'general': [
            {"message": "🤔 Analyzing your question...", "duration": 700},
            {"message": "💭 Processing with AI reasoning...", "duration": 800},
            {"message": "✨ Preparing the best response...", "duration": 500},
        ],
    }
    
    # ============================================================
    # RESPONSE DATABASE - Rich, varied, brand-aware responses
    # ============================================================
    RESPONSES = {
        # ---------- GREETINGS ----------
        'greeting': [
            "Hello! 👋 I'm your **CourseCart AI Assistant** — here to help you discover vocational courses, understand payments, and navigate the platform. What can I help you with today?",
            "Hi there! 😊 Welcome to **CourseCart**! I'm your AI guide. Ask me about our courses, how to enroll, payment methods, or anything about the platform!",
            "Karibu! 👋 I'm the CourseCart AI Assistant. Whether you want to learn Plumbing, Electrical, Tailoring, or become an instructor — I'm here to help! 🎓",
        ],
        
        # ---------- ABOUT COURSECART ----------
        'about': [
            "**CourseCart** 📚 is Tanzania's online vocational training platform. We connect unemployed youth with expert instructors offering affordable courses (TZS 20,000-50,000) in Plumbing, Electrical, Tailoring, Welding, Carpentry, and more. Built by a team of 5 dedicated developers, CourseCart makes skills training accessible anywhere, anytime! 🌍\n\nVisit us at: coursecart.pythonanywhere.com",
            
            "**CourseCart** was born from a simple mission: make vocational training affordable and accessible to all Tanzanian youth. 🇹🇿 Our platform offers certified courses in skilled trades, with flexible payment options including M-Pesa, Tigo Pesa, and bank cards. We're proud to have helped hundreds of students gain employable skills! 🎓",
        ],
        
        # ---------- TEAM ----------
        'team': [
            "CourseCart was built by an amazing team of 5 developers:\n\n"
            "📋 **Neema Manoza** — Project Manager\n"
            "💻 **Godfrey Augustino** — Backend Developer (Django architecture, databases, payment systems)\n"
            "🎨 **Modesti Imam** — Frontend Developer (responsive UI, JavaScript, HTML/CSS)\n"
            "🖌️ **Mustapha Lameck** — UI/UX Designer (visual design, wireframes, color schemes)\n"
            "📊 **Doreen Aloyce** — Business Analyst (market research, requirements, use cases)\n\n"
            "Together, we built this platform to help Tanzanian youth learn vocational skills! 🚀",
            
            "Our development team consists of 5 talented individuals:\n\n"
            "👨‍💼 **Neema Manoza** leads as Project Manager, ensuring everything runs smoothly.\n"
            "⚙️ **Godfrey Augustino** handles all backend magic — Django, databases, and payments.\n"
            "🎨 **Modesti Imam** creates the beautiful interfaces you see.\n"
            "🖌️ **Mustapha Lameck** designed the Teal & Amber visual identity.\n"
            "📊 **Doreen Aloyce** analyzed market needs to shape our features.\n\n"
            "We're proud of what we built! 🎉",
        ],
        
        # ---------- TEAM MEMBER SPECIFIC ----------
        'neema': [
            "📋 **Neema Manoza** is our exceptional Project Manager! She oversaw the entire CourseCart development — planning timelines, allocating resources, ensuring quality standards, and coordinating between all team members and stakeholders. Her leadership kept us on track! 🎯",
        ],
        'godfrey': [
            "💻 **Godfrey Augustino** is our brilliant Backend Developer! He architected the entire Django system — custom user models, course management, payment simulation, notification systems, and all 5 backend modules. The robust platform you're using? That's Godfrey's work! ⚡",
        ],
        'modesti': [
            "🎨 **Modesti Imam** is our talented Frontend Developer! He built all the responsive templates, JavaScript interactions, and user interfaces across 20+ pages. Every button, card, and animation you see is crafted by Modesti! ✨",
        ],
        'mustapha': [
            "🖌️ **Mustapha Lameck** is our creative UI/UX Designer! He created the entire visual identity — the Teal (#0D9488) and Amber (#F59E0B) color scheme, all wireframes, prototypes, and ensured the platform is intuitive and beautiful on every device! 🎨",
        ],
        'doreen': [
            "📊 **Doreen Aloyce** is our insightful Business Analyst! She conducted market research with 120+ Tanzanian youth, defined business requirements, created use cases, and ensured CourseCart addresses real user needs. Her analysis shaped our entire platform! 📈",
        ],
        
        # ---------- COURSES ----------
        'courses': [
            "🎓 CourseCart offers vocational training in:\n\n"
            "🔧 **Plumbing & Pipe Fitting**\n"
            "⚡ **Electrical Installation**\n"
            "🧵 **Tailoring & Fashion Design**\n"
            "🪚 **Carpentry & Joinery**\n"
            "🔥 **Welding & Metal Fabrication**\n"
            "🧱 **Masonry & Brickwork**\n"
            "☀️ **Solar Panel Installation**\n"
            "❄️ **Refrigeration & AC**\n"
            "💻 **Computer & IT Skills**\n\n"
            "All courses include video lessons, PDF notes, and completion certificates. Visit /courses/ to browse! 📚",
            
            "We have 15+ course categories! Our most popular are Plumbing 🔧, Electrical ⚡, and Tailoring 🧵. Each course is designed by expert instructors with video lessons, downloadable PDFs, and hands-on projects. Prices range from TZS 20,000-50,000 — and some are FREE! 🆓\n\nBrowse all courses at /courses/",
        ],
        
        # ---------- PAYMENTS ----------
        'payments': [
            "💳 Payment at CourseCart is flexible:\n\n"
            "📱 **Mobile Money**: M-Pesa, Tigo Pesa, Airtel Money\n"
            "💳 **Bank Cards**: Visa, Mastercard\n"
            "💵 **Cash Payment**: At authorized agents\n\n"
            "Courses cost TZS 20,000-50,000. We also have FREE courses! 🆓\n"
            "Note: Payments are currently simulated for testing purposes.",
            
            "You can pay via M-Pesa 📱, Tigo Pesa, bank card 💳, or cash 💵. Most courses are TZS 20,000-50,000 — very affordable compared to traditional training centers (TZS 300,000+). We also offer free courses! Payment is secure and simulated for now.",
        ],
        
        # ---------- ENROLLMENT ----------
        'enrollment': [
            "📝 Enrolling is quick and easy:\n\n"
            "1️⃣ Browse courses at **/courses/**\n"
            "2️⃣ Click on a course you like\n"
            "3️⃣ Hit the **'Enroll Now'** button\n"
            "4️⃣ Complete payment (or get instant access for free courses)\n"
            "5️⃣ Start learning immediately! 🎓\n\n"
            "Your progress is saved automatically!",
            
            "Ready to start? 🚀 Go to /courses/, pick a course, click 'Enroll Now', complete payment, and you're in! Free courses give instant access. It takes under 2 minutes to start learning!",
        ],
        
        # ---------- CERTIFICATES ----------
        'certificates': [
            "📜 Yes! When you complete **100% of a course's lessons**, you automatically earn a **Certificate of Completion**. This certificate can be used for job applications, self-employment credentials, or further training. Make sure the course has certificates enabled (most do)! 🎓",
            
            "Complete all lessons in any course, and you'll receive a 📜 Certificate of Completion automatically! It's proof of your new skills — great for employers or starting your own business. Keep learning! 💪",
        ],
        
        # ---------- INSTRUCTOR ----------
        'instructor': [
            "👨‍🏫 Want to teach on CourseCart? Here's how:\n\n"
            "1️⃣ Register as an instructor at **/accounts/register/instructor/**\n"
            "2️⃣ Create your course (title, description, price)\n"
            "3️⃣ Add lessons (YouTube videos, PDFs, or your own videos)\n"
            "4️⃣ Publish and start earning! 💰\n\n"
            "Instructors earn from every student enrollment. Share your vocational skills with Tanzania! 🇹🇿",
            
            "Join as an instructor! 🚀 Register at /accounts/register/instructor/, create courses with video lessons & PDFs, set your price, and earn when students enroll. It's free to start! Share your expertise in Plumbing, Electrical, Tailoring, or any trade.",
        ],
        
        # ---------- PLATFORM HELP ----------
        'platform_help': [
            "🗺️ Here's your CourseCart navigation guide:\n\n"
            "📊 **Dashboard**: /dashboard/student/ or /dashboard/instructor/\n"
            "📚 **Browse Courses**: /courses/\n"
            "📖 **My Courses**: /courses/my-courses/\n"
            "💳 **Payments**: /payments/history/\n"
            "🔔 **Notifications**: /notifications/\n"
            "⚙️ **Settings**: Sidebar → Edit Profile\n\n"
            "What are you looking for? 😊",
        ],
        
        # ---------- GENERAL ----------
        'general': [
            "I'm here to help with anything CourseCart-related! 😊 You can ask me about:\n\n"
            "📚 Available courses and categories\n"
            "💰 Payment methods and pricing\n"
            "📝 How to enroll in courses\n"
            "📜 Certificates and completion\n"
            "👨‍🏫 Becoming an instructor\n"
            "👥 Our development team\n"
            "🏢 About CourseCart\n\n"
            "What would you like to know?",
        ],
    }
    
    # ============================================================
    # INTENT CLASSIFICATION
    # ============================================================
    @staticmethod
    def classify_intent(message):
        """Advanced intent classification with multi-keyword matching."""
        message_lower = message.lower().strip()
        
        patterns = {
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'how are you', 'whats up', 'greetings'],
            'about': ['about coursecart', 'what is coursecart', 'tell me about', 'who built', 'platform', 'website'],
            'team': ['team', 'who developed', 'developers', 'who made', 'who created', 'group', 'members'],
            'neema': ['neema', 'project manager', 'manager'],
            'godfrey': ['godfrey', 'backend', 'backend developer'],
            'modesti': ['modesti', 'frontend', 'frontend developer'],
            'mustapha': ['mustapha', 'uiux', 'ui/ux', 'designer', 'ui designer'],
            'doreen': ['doreen', 'business analyst', 'analyst'],
            'courses': ['course', 'courses', 'available', 'offer', 'learn', 'study', 'training', 'skill', 'skills', 'plumbing', 'electrical', 'tailoring', 'welding', 'carpentry', 'category', 'what do you', 'what can i'],
            'payments': ['pay', 'payment', 'price', 'cost', 'fee', 'amount', 'mpesa', 'tigo', 'airtel', 'mobile money', 'bank', 'card', 'cash', 'tzs', 'free'],
            'enrollment': ['enroll', 'enrollment', 'join', 'register', 'sign up', 'start', 'begin', 'take course', 'get started', 'how do i'],
            'certificates': ['certificate', 'certification', 'certified', 'completion', 'credential', 'qualification'],
            'instructor': ['teach', 'teaching', 'instructor', 'create course', 'become', 'upload', 'publish', 'earn'],
            'platform_help': ['how to', 'where', 'find', 'navigate', 'dashboard', 'profile', 'settings', 'account', 'login', 'password', 'help', 'support', 'contact'],
        }
        
        scores = {}
        for intent, keywords in patterns.items():
            score = sum(1 for kw in keywords if kw in message_lower)
            if score > 0:
                scores[intent] = score / len(keywords)
        
        if scores:
            best = max(scores, key=scores.get)
            return best, round(scores[best], 2)
        
        return 'general', 0.1
    
    # ============================================================
    # MAIN RESPONSE METHOD
    # ============================================================
    @staticmethod
    def get_smart_response(user_message, user_name='Student', user_role='student'):
        """
        Get intelligent response with thinking simulation.
        """
        start_time = time.time()
        
        # Step 1: Classify intent
        intent, confidence = ChatbotService.classify_intent(user_message)
        
        # Step 2: Get thinking sequence
        thinking_steps = ChatbotService.THINKING_SEQUENCES.get(
            intent, 
            ChatbotService.THINKING_SEQUENCES['general']
        )
        
        # Step 3: Get response
        strategy = 'template'
        response_text = None
        
        # Try Gemini API
        try:
            context = ChatbotService._get_course_context()
            gemini_result = ChatbotService._call_gemini(user_message, user_name, user_role, context)
            if gemini_result and gemini_result.get('response'):
                response_text = gemini_result['response']
                strategy = 'gemini_api'
        except Exception:
            pass
        
        # Fallback to template
        if not response_text:
            responses = ChatbotService.RESPONSES.get(intent, ChatbotService.RESPONSES['general'])
            response_text = random.choice(responses)
        
        # Step 4: Record interaction
        interaction_id = None
        try:
            from .models import ChatInteraction
            interaction = ChatInteraction.objects.create(
                user_message=user_message,
                bot_response=response_text,
                intent_detected=intent,
                strategy_used=strategy,
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            interaction_id = interaction.id
        except Exception:
            pass
        
        return {
            'response': response_text,
            'intent': intent,
            'confidence': confidence,
            'strategy': strategy,
            'interaction_id': interaction_id,
            'thinking_steps': thinking_steps,
        }
    
    # ============================================================
    # GEMINI API CALL
    # ============================================================
    @staticmethod
    def _call_gemini(user_message, user_name, user_role, context=''):
        """Call Gemini API with CourseCart-specific system prompt."""
        api_key = getattr(settings, 'GEMINI_API_KEY', os.environ.get('GEMINI_API_KEY', ''))
        if not api_key:
            return None
        
        try:
            import requests
            
            system_prompt = f"""You are the CourseCart AI Assistant for an online vocational training platform in Tanzania.

ABOUT COURSECART:
- Platform: coursecart.pythonanywhere.com
- Mission: Affordable vocational training for Tanzanian youth
- Courses: Plumbing, Electrical, Tailoring, Carpentry, Welding, Masonry, Solar, IT Skills
- Pricing: TZS 20,000-50,000 (some free)
- Payments: M-Pesa, Tigo Pesa, Bank Cards, Cash
- Built by: 5 developers (Neema Manoza-PM, Godfrey Augustino-Backend, Modesti Imam-Frontend, Mustapha Lameck-UI/UX, Doreen Aloyce-Business Analyst)

YOUR PERSONALITY:
- Friendly, encouraging, professional
- Use markdown formatting for readability
- Keep responses 3-5 sentences unless asked for details
- Use relevant emojis
- Mention /courses/ for browsing courses

CONTEXT: {context}
USER: {user_name} ({user_role})"""
            
            url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}'
            payload = {
                'contents': [{'parts': [{'text': system_prompt}, {'text': user_message}]}],
                'generationConfig': {'temperature': 0.7, 'maxOutputTokens': 400}
            }
            
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get('candidates', [])
                if candidates:
                    parts = candidates[0].get('content', {}).get('parts', [])
                    if parts:
                        return {'response': parts[0].get('text', '').strip()}
            return None
        except Exception:
            return None
    
    @staticmethod
    def _get_course_context():
        """Get current course information for context."""
        try:
            from apps.courses.models import Course, Category
            cats = Category.objects.all()[:5]
            courses = Course.objects.filter(status='published')[:5]
            parts = []
            if cats:
                parts.append("Categories: " + ", ".join(f"{c.name}" for c in cats))
            if courses:
                parts.append("Courses: " + ", ".join(f"{c.title}" for c in courses))
            return ' | '.join(parts) if parts else ''
        except Exception:
            return ''