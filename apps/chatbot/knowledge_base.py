"""
Self-learning knowledge base that improves from interactions.
"""
import json
import os
from django.utils import timezone
from .models import KnowledgeEntry, ChatInteraction


class KnowledgeBase:
    """
    Manages the chatbot's knowledge, learns from interactions,
    and improves response quality over time.
    """
    
    @staticmethod
    def search(query, intent=None, limit=5):
        """
        Search the knowledge base for matching entries.
        """
        from django.db.models import Q
        
        queryset = KnowledgeEntry.objects.filter(is_active=True)
        
        if intent:
            queryset = queryset.filter(intent=intent)
        
        # Search by keywords
        words = query.lower().split()
        q_objects = Q()
        for word in words:
            q_objects |= Q(question_pattern__icontains=word)
            q_objects |= Q(keywords__icontains=word)
        
        queryset = queryset.filter(q_objects)
        
        # Order by success rate
        return queryset.order_by('-success_count', '-usage_count')[:limit]
    
    @staticmethod
    def learn_from_interaction(interaction_id):
        """
        Learn from a successful interaction.
        Updates knowledge base with new patterns.
        """
        try:
            interaction = ChatInteraction.objects.get(id=interaction_id)
            
            if not interaction.was_helpful:
                return None
            
            # Check if similar entry exists
            existing = KnowledgeEntry.objects.filter(
                intent=interaction.intent_detected,
                is_active=True
            ).first()
            
            if existing:
                # Update existing entry
                existing.usage_count += 1
                existing.success_count += 1
                existing.last_used_at = timezone.now()
                
                # Add response variation if new
                variations = existing.response_variations or []
                if not any(v.get('text') == interaction.bot_response for v in variations):
                    variations.append({
                        'text': interaction.bot_response,
                        'added_at': timezone.now().isoformat(),
                        'success_count': 1
                    })
                existing.response_variations = variations
                existing.save()
                return existing
            
            # Create new entry
            entry = KnowledgeEntry.objects.create(
                question_pattern=interaction.user_message[:500],
                keywords=','.join(interaction.user_message.lower().split()[:10]),
                intent=interaction.intent_detected or 'general',
                response_variations=[{
                    'text': interaction.bot_response,
                    'added_at': timezone.now().isoformat(),
                    'success_count': 1
                }],
                usage_count=1,
                success_count=1,
                last_used_at=timezone.now()
            )
            return entry
            
        except ChatInteraction.DoesNotExist:
            return None
    
    @staticmethod
    def seed_initial_knowledge():
        """
        Seed the knowledge base with initial Q&A pairs.
        """
        initial_data = [
            {
                'question_pattern': 'what courses are available',
                'keywords': 'courses,available,offer,learn',
                'intent': 'courses',
                'response_variations': [
                    {'text': 'We offer Plumbing 🔧, Electrical ⚡, Tailoring 🧵, Welding 🔥, Carpentry 🪚, and more! All with certificates. Browse /courses/!'},
                    {'text': 'Our courses include Plumbing, Electrical, Tailoring, Welding, Carpentry, and Solar Installation. Visit /courses/ to see all!'},
                    {'text': 'You can learn Plumbing, Electrical work, Tailoring, Carpentry, Welding, and more on CourseCart. Check /courses/!'},
                ]
            },
            {
                'question_pattern': 'how do i pay',
                'keywords': 'pay,payment,mpesa,tigo,cost',
                'intent': 'payments',
                'response_variations': [
                    {'text': 'Pay via 📱 M-Pesa, Tigo Pesa, 💳 Bank Card, or 💵 Cash. Courses cost TZS 20,000-50,000. Free courses available! 🆓'},
                    {'text': 'We accept Mobile Money, Bank Cards, and Cash. Most courses are TZS 20,000-50,000. Payment is simulated for testing.'},
                    {'text': 'Choose Mobile Money, Bank Card, or Cash payment. Prices are affordable — TZS 20,000-50,000 per course.'},
                ]
            },
            {
                'question_pattern': 'how to enroll',
                'keywords': 'enroll,join,register,start',
                'intent': 'enrollment',
                'response_variations': [
                    {'text': 'Browse /courses/, click Enroll Now, complete payment, and start learning! For free courses, access is instant. 🎓'},
                    {'text': 'Find a course at /courses/, hit Enroll Now, pay if needed, and you\'re in! It takes under 2 minutes. 🚀'},
                    {'text': 'Go to /courses/, pick a course, enroll, pay, and start learning immediately! Simple and fast! ✅'},
                ]
            },
        ]
        
        created_count = 0
        for data in initial_data:
            if not KnowledgeEntry.objects.filter(question_pattern=data['question_pattern']).exists():
                KnowledgeEntry.objects.create(**data)
                created_count += 1
        
        return created_count