import os
import json
from google import genai
from google.genai import types

# ⚠️ Yahan apni nayi API Key daal lein
API_KEY = "Add Your Gemini API Key"
client = genai.Client(api_key=API_KEY)

# 🔥 FEW-SHOT PROMPT (AI ko examples ke sath sikhana)
DATASET_SCHEMA_PROMPT = """
You are an expert AI Customer Support Assistant for an e-commerce enterprise. 
You must deeply understand English, Urdu, and Roman Urdu.

Schema:
- Categories: ['Technical Support', 'Returns', 'Logistics', 'Sales', 'Account Support', 'Payments', 'Other']
- Sentiments: ['Positive', 'Neutral', 'Negative']

RULES & EXAMPLES:
1. If user says "hi, mujhe mera product abi tk ni pocha", it is a Logistics issue (Shipping Inquiry) with Negative sentiment.
2. If user says "hi how are you?", it is 'Account Support' category, 'Greeting' intent, and Neutral sentiment.
3. NEVER classify a message as "Greeting" if it contains a complaint about delivery, product, or money.

Return a strict JSON object with keys: "intent", "category", "sentiment", "summary".
"""

def smart_fallback_analyzer(message: str):
    msg_lower = message.lower()
    
    if any(w in msg_lower for w in ['payment', 'deducted', 'charged', 'card', 'money', 'fee', 'wallet', 'paise']):
        category = "Payments"
        intent = "Payment Issue"
    elif any(w in msg_lower for w in ['transit', 'shipping', 'package', 'delivery', 'arrived', 'stuck', 'tracking', 'deliver nahi hua', 'recived ni huwa', 'pocha', 'pohncha', 'kahan', 'kaha']):
        category = "Logistics"
        intent = "Shipping Inquiry"
    elif any(w in msg_lower for w in ['dark mode', 'app', 'crash', 'login', 'error', 'bug', 'click', 'loading', 'masla']):
        category = "Technical Support"
        intent = "Bug Report"
    elif any(w in msg_lower for w in ['return', 'refund', 'damaged', 'wrong product', 'exchange', 'wapas', 'kharab']):
        category = "Returns"
        intent = "Return Request"
    elif any(w in msg_lower for w in ['hack', 'scam', 'secure', 'stolen', 'lost', 'recover', 'unauthorized', 'password', 'chori']):
        category = "Account Support"
        intent = "Account Security / Recovery"
    else:
        category = "Account Support"
        intent = "Greeting"
        
    if any(w in msg_lower for w in ['nobody is helping', 'upset', 'angry', 'crashing', 'stuck', 'worst', 'hack', 'scam', 'immediate', 'urgent', 'lost', 'damaged', 'deliver nahi hua', 'kharab', 'ghussa', 'refund', 'abi tk', 'abhi tak', 'nahi aaya', 'pocha']):
        sentiment = "Negative"
    elif any(w in msg_lower for w in ['thanks', 'good', 'great', 'awesome', 'shukriya', 'behtareen']):
        sentiment = "Positive"
    else:
        sentiment = "Neutral"
        
    return {
        "intent": intent,
        "category": category,
        "sentiment": sentiment,
        "summary": f"Customer reported an issue regarding {intent.lower()}."
    }

def analyze_customer_ticket(message: str):
    full_prompt = f"""
    {DATASET_SCHEMA_PROMPT}
    Analyze this incoming customer message:
    "{message}"
    """
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print("⚠️ API Quota/Error encountered. Switching to Smart Fallback Parser...")
        return smart_fallback_analyzer(message)