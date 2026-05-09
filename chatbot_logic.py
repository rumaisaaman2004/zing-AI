import re
import random
import os
from dotenv import load_dotenv # type: ignore
from groq import Groq # type: ignore

# Load environment variables
load_dotenv()

# Initialize Groq client
try:
    groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    GROQ_AVAILABLE = True
    print("✅ Groq AI Connected Successfully")
except Exception as e:
    GROQ_AVAILABLE = False
    print(f"⚠️  Groq AI Not Available: {e}")

class Chatbot:
    def __init__(self):
        # Legal categories for Zakoota
        self.categories = {
            'family': ['divorce', 'marriage', 'child custody', 'alimony'],
            'criminal': ['theft', 'assault', 'fraud', 'murder'],
            'property': ['land dispute', 'property sale', 'rent agreement'],
            'corporate': ['contract', 'company registration', 'tax'],
            'cyber': ['cyber crime', 'data theft', 'online fraud']
        }
        
        # Common legal questions and answers (FAST Responses)
        self.legal_qa = {
            # Family Law
            'divorce': 'In Pakistan, divorce can be through Talaq (husband), Khula (wife), or court decree. 90-day reconciliation period required.',
            'khula': 'Khula is wife-initiated divorce. File in family court with reasons. Return Mehr to husband.',
            'nikah': 'Nikah requires CNIC, witnesses, nikah registrar, and agreement on Mehr amount.',
            'child custody': 'Child custody decided by family court based on child welfare. Mothers preferred for young children.',
            'maintenance': 'Wife can claim maintenance under Muslim Family Laws Ordinance 1961.',
            
            # Criminal Law
            'fir': 'FIR (First Information Report) filed at police station. Get copy with FIR number.',
            'bail': 'Bail applications filed in relevant court. Depends on offense severity.',
            'murder': 'Murder case under Section 302 PPC. Death penalty or life imprisonment.',
            'theft': 'Theft under Section 378 PPC. Punishment up to 3 years imprisonment.',
            'fraud': 'Fraud cases under Section 420 PPC. Need documentary evidence.',
            
            # Property Law
            'property sale': 'Property sale requires registry at patwari office, stamp paper, and mutation.',
            'rent agreement': 'Rent agreement should be on stamp paper with terms, duration, and security deposit.',
            'land dispute': 'Land disputes resolved by civil court. Need ownership documents like Fard.',
            'succession certificate': 'Succession certificate obtained from civil court for inheritance.',
            
            # Business Law
            'company registration': 'Company registered with SECP. Need company name, directors, and memorandum.',
            'sales tax': 'Sales tax registration with FBR if turnover exceeds Rs. 10 million.',
            'income tax': 'File income tax returns by September 30. NTN required.',
            'labor law': 'Minimum wage Rs. 32,000 (2024). Provinces have separate labor laws.',
            
            # Cyber Law
            'cyber crime': 'Cyber crimes under PECA 2016. Report to FIA cyber crime wing.',
            'online harassment': 'Online harassment punishable under PECA. Screenshot evidence required.',
            
            # General Legal
            'power of attorney': 'Power of attorney on stamp paper. Can be general or special.',
            'affidavit': 'Affidavit made before oath commissioner or notary public.',
            'court fee': 'Court fees vary by case type and claim amount. Check court fee calculator.',
            'case filing': 'Case filed through lawyer. Need plaint, documents, and court fees.',
            
            # Lawyer Practice
            'case laws': 'Check PLD (Pakistan Legal Decisions) or SCMR for latest case laws.',
            'legal research': 'Use Pakistan Law Site or PLJ for legal research.',
            'client consultation': 'Always take consultation fee and issue receipt.',
            
            # Quick Responses
            'hello': 'Hello! I\'m Zing AI Legal Assistant. How can I help you today?',
            'hi': 'Hi! Need legal assistance or looking for a lawyer?',
            'thanks': 'You\'re welcome! Let me know if you need further assistance.',
            'bye': 'Goodbye! Feel free to return if you need legal help.',
            
            'default': 'I understand your query. Let me provide detailed information.'
        }
        
        # Greeting patterns
        self.greetings = ['hello', 'hi', 'hey', 'assalam', 'salam', 'good morning', 'good afternoon']
        self.goodbyes = ['bye', 'goodbye', 'exit', 'quit', 'see you']

    def _get_groq_response(self, message, user_type):
        """Get smart response from Groq for any question"""
        if not GROQ_AVAILABLE:
            return "For detailed legal advice, please consult a verified lawyer on Zakoota."
        
        try:
            # System prompt based on user type
            if user_type == 'lawyer':
                system_prompt = "You are a senior Pakistani lawyer with 20+ years experience. Provide accurate legal information with relevant Pakistan Penal Code sections, case laws, and practical advice. Be professional and detailed."
            else:
                system_prompt = "You are Zing AI Legal Assistant, helping users with Pakistan laws. Provide accurate, simple explanations. If complex, recommend consulting a lawyer. Always cite relevant laws if known."
            
            # Adjust response length based on keywords
            message_lower = message.lower()
            if 'detail' in message_lower or 'explain' in message_lower or 'step by step' in message_lower:
                max_tokens = 350
                instruction = "Provide detailed, comprehensive explanation with examples from Pakistan law."
            elif 'brief' in message_lower or 'short' in message_lower or 'summary' in message_lower:
                max_tokens = 100
                instruction = "Provide concise 1-2 line summary."
            else:
                max_tokens = 200
                instruction = "Provide clear 2-3 line answer with key points."
            
            response = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{instruction}\n\nQuestion: {message}\n\nProvide answer according to Pakistan laws:"}
                ],
                model="llama-3.1-8b-instant",
                max_tokens=max_tokens,
                temperature=0.3,
                timeout=10
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Groq API Error: {e}")
            return "I recommend consulting a verified lawyer on Zakoota for accurate legal advice."

    def get_response(self, user_message, user_type, db=None):
        """Main function to get chatbot response"""
        user_message_lower = user_message.lower().strip()
        
        # 1. Check for greetings (FAST) - match as whole words
        if any(greet == user_message_lower or greet + ' ' in user_message_lower for greet in self.greetings):
            return self._greet_user(user_type)
        
        # 2. Check for goodbyes (FAST) - match as whole words
        if any(bye == user_message_lower or bye + ' ' in user_message_lower for bye in self.goodbyes):
            return "Goodbye! Feel free to return if you need more legal help."
        
        # 3. Check quick responses dictionary (FAST) - only for exact or very simple queries
        if user_message_lower in self.legal_qa:
            return self.legal_qa[user_message_lower]
        
        # 4. Check if this is a detailed/complex question that needs Groq AI
        # Keywords that indicate user wants detailed explanation
        detail_keywords = ['detail', 'explain', 'step by step', 'how to', 'process', 'guide', 'procedure', 'full']
        is_detailed_question = any(keyword in user_message_lower for keyword in detail_keywords)
        
        # If it's a detailed question, skip quick responses and go straight to AI
        if is_detailed_question:
            if user_type == 'client':
                return self._handle_general_query(user_message)
            elif user_type == 'lawyer':
                return self._handle_lawyer_query(user_message)
            else:
                return self._handle_general_query(user_message)
        
        # 5. Route based on user type
        if user_type == 'client':
            return self._handle_client_query(user_message, db)
        elif user_type == 'lawyer':
            return self._handle_lawyer_query(user_message)
        else:
            return self._handle_general_query(user_message)

    def _greet_user(self, user_type):
        """Generate greeting based on user type"""
        if user_type == 'client':
            return "Hello! I'm Zing AI Legal Assistant. How can I help you find a lawyer today?"
        elif user_type == 'lawyer':
            return "Hello Counselor! How can I assist you with legal information today?"
        else:
            return "Hello! I'm Zing AI Legal Assistant. How can I help you?"

    def _handle_client_query(self, message, db):
        """Handle client queries - answer questions first, then offer lawyers"""
        message_lower = message.lower()
        
        # Check if asking for lawyer specifically
        lawyer_keywords = ['lawyer', 'advocate', 'attorney', 'counsel']
        is_asking_for_lawyer = any(keyword in message_lower for keyword in lawyer_keywords)
        
        if is_asking_for_lawyer:
            # Extract legal category
            category = self._extract_category(message)
            
            if db:
                # Get lawyers from Firebase
                lawyers = self._get_lawyers_from_db(category, db)
                if lawyers:
                    return self._format_lawyer_response(lawyers, category)
            
            # Mock response if no DB
            return f"I found 3 {category} lawyers for you: 1) Ali Khan (4.5★) 2) Sara Ahmed (4.8★) 3) Ahmed Raza (4.3★). You can view their profiles in the app."
        
        # For all other questions, provide legal info with AI
        return self._handle_general_query(message)

    def _handle_lawyer_query(self, message):
        """Handle lawyer queries with AI"""
        # First check simple rules (FAST) - only exact matches
        message_lower = message.lower().strip()
        if message_lower in self.legal_qa:
            return self.legal_qa[message_lower]
        
        # Use Groq AI for lawyer-specific queries
        return self._get_groq_response(message, user_type='lawyer')

    def _handle_general_query(self, message):
        """Handle ALL legal questions with AI"""
        # First check simple rules (FAST common questions) - only exact matches
        message_lower = message.lower().strip()
        if message_lower in self.legal_qa:
            return self.legal_qa[message_lower]
        
        # For ALL other questions, use Groq AI
        return self._get_groq_response(message, user_type='client')

    def _extract_category(self, message):
        """Extract legal category from user message"""
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in message.lower():
                    return category
        return 'general'

    def _get_lawyers_from_db(self, category, db):
        """Get lawyers from Firebase filtered by category"""
        try:
            lawyers_ref = db.collection('lawyers')
            query = lawyers_ref.where('specialization', '==', category)
            docs = query.limit(5).stream()
            
            lawyers = []
            for doc in docs:
                lawyer_data = doc.to_dict()
                lawyer_data['id'] = doc.id
                lawyers.append(lawyer_data)
            
            return lawyers
        except:
            return None

    def _format_lawyer_response(self, lawyers, category):
        """Format lawyer list into readable response"""
        if not lawyers:
            return f"Sorry, no {category} lawyers available at the moment."
        
        response = f"I found {len(lawyers)} {category} lawyers:\n"
        for i, lawyer in enumerate(lawyers[:3], 1):
            response += f"{i}) {lawyer.get('name', 'Lawyer')} - {lawyer.get('experience', 'N/A')} years exp, {lawyer.get('rating', 'N/A')}★\n"
        
        response += "You can view detailed profiles and contact them through the app."
        return response

# Create global chatbot instance
chatbot = Chatbot()

def get_response(user_message, user_type, db=None):
    """Public function to get chatbot response"""
    return chatbot.get_response(user_message, user_type, db)