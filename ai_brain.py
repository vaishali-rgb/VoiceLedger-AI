from google import genai
from google.genai import types
import json
import re
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-flash-lite-latest"


def parse_transaction(user_text: str) -> dict:
    """
    Given natural speech like "bechta hun 5 kg aata 100 rupees mein",
    use Gemini to extract structured transaction data.

    Returns dict:
      { type, item, item_hindi, quantity, unit, price, confidence }
    """
    prompt = f"""
You are a smart transaction parser for an Indian kirana (grocery) store.
The shopkeeper speaks in Hindi, Gujarati, or English — sometimes mixed.

Extract details from this voice command: "{user_text}"

Return ONLY a valid JSON object (no markdown, no explanation) with:
- "type": "sale", "expense", "query", or "unknown"
- "item": item name in English (e.g. "flour", "oil", "sugar")
- "item_hindi": item name as spoken (e.g. "aata", "tel", "cheeni")
- "quantity": number or null
- "unit": "kg", "litre", "piece", "packet", "dozen" or null
- "price": total price in Indian Rupees as a number, or null
- "confidence": "high", "medium", or "low"

Examples:
"bechta hun 5 kg aata 100 rupees mein"
→ {{"type":"sale","item":"flour","item_hindi":"aata","quantity":5,"unit":"kg","price":100,"confidence":"high"}}

"kharida 2 litre tel 180 rupaye ka"
→ {{"type":"expense","item":"oil","item_hindi":"tel","quantity":2,"unit":"litre","price":180,"confidence":"high"}}

"aaj kitna profit hua"
→ {{"type":"query","item":null,"item_hindi":null,"quantity":null,"unit":null,"price":null,"confidence":"high"}}

"sold 12 eggs for 60 rupees"
→ {{"type":"sale","item":"eggs","item_hindi":"anda","quantity":12,"unit":"piece","price":60,"confidence":"high"}}

Now parse: "{user_text}"
"""
    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        raw = response.text.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        return json.loads(raw)
    except (json.JSONDecodeError, Exception) as e:
        print(f"⚠️  Gemini parse error: {e}")
        return {
            "type": "unknown", "item": None, "item_hindi": None,
            "quantity": None, "unit": None, "price": None,
            "confidence": "low"
        }


def answer_business_query(question: str, db_context: str) -> str:
    """
    RAG: answer shopkeeper's questions using real data from SQLite.
    db_context = today's business data as plain text.
    Returns a short, friendly reply in the same language as the question.
    """
    prompt = f"""
You are VoiceLedger AI — a friendly, helpful business assistant for
Indian kirana shopkeepers. You speak in simple Hindi by default,
but match the user's language (Hindi / Gujarati / English).

Use ₹ for rupees. Keep answers short (2–3 sentences max).
Be warm and encouraging.

Today's real business data from the database:
{db_context}

Shopkeeper's question: "{question}"

Answer helpfully based on the data above.
"""
    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text.strip()
    except Exception as e:
        return f"Maafi kijiye, abhi answer nahi de sakta. ({e})"


def generate_daily_report(db_context: str) -> str:
    """Generate a full spoken daily business report in Hindi."""
    prompt = f"""
You are VoiceLedger AI. Generate a short, friendly daily business
summary in Hindi for a kirana shopkeeper. Use ₹ for rupees.
Make it sound like a helpful assistant reading a report aloud.
Keep it under 100 words.

Business data:
{db_context}
"""
    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text.strip()
    except Exception as e:
        return "Report generate karne mein dikkat aayi."
