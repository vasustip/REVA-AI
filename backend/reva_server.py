from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()
import requests
import re

from memory_store import add_to_history, get_last_messages, update_traits

app = Flask(__name__)
CORS(app)

import os
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama3-70b-8192"

def convert_to_transliteration(text):
    """Convert Hindi text to English transliteration using simple mapping"""
    if re.search(r'[a-zA-Z]', text):
        return text
        
    mapping = {
        'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo',
        'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'क': 'k', 'ख': 'kh',
        'ग': 'g', 'घ': 'gh', 'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh',
        'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n', 'त': 't',
        'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n', 'प': 'p', 'फ': 'ph',
        'ब': 'b', 'भ': 'bh', 'म': 'm', 'य': 'y', 'र': 'r', 'ल': 'l',
        'व': 'v', 'श': 'sh', 'ष': 'sh', 'स': 's', 'ह': 'h', 'क्ष': 'ksh',
        'त्र': 'tr', 'ज्ञ': 'gya', '़': '', 'ः': 'h', 'ं': 'm', 'ँ': 'n',
        'ा': 'a', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo', 'े': 'e',
        'ै': 'ai', 'ो': 'o', 'ौ': 'au', '्': '', 'ृ': 'ri', 'ऋ': 'ri'
    }
    
    converted = []
    for char in text:
        converted.append(mapping.get(char, char))
    return ''.join(converted)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_id = data.get("user_id", "default_user")
    user_message = data.get("message", "")
    mode = data.get("mode", "logical")
    language = data.get("language", "english")

    history = get_last_messages(user_id)
    traits = update_traits(user_id, user_message)

    intro = ""
    if language == "hindi":
        intro += (
            "Tum REVA ho, ek AI jo mental health mein logon ki madad karti hai. "
            "Tumhara lehja prem aur samvedansheel hai. Tum spasht tareeke se baat karti ho. "
            "Zarurat padne par sawal poochti ho. "
            "**Important: Tumhe hamesha Roman Hindi mein jawab dena hai - Hindi shabdon ko English letters mein likhna hai.** "
        )
    else:
        intro += (
            "You are REVA, a wise and caring AI guide. You help people with depression, frustration, and mental health struggles.\n"
            "Your tone is gentle, kind, and supportive. Use logical reasoning with a loving touch.\n"
            "Structure your responses in bullet points or clear sections when needed, like ChatGPT.\n"
            "Ask thoughtful questions only when it makes sense to continue the conversation.\n"
        )

    if mode == "spiritual":
        intro += (
            "Speak with spiritual wisdom like Lord Krishna when appropriate. "
            "You may use spiritual metaphors and references when they are emotionally helpful.\n"
        )
    elif mode == "logical":
        intro += (
            "Be grounded in logic and reason. Avoid unnecessary spiritual or emotional language unless it's helpful.\n"
        )

    if traits:
        intro += f"\nThis user seems to be: {', '.join(traits)}.\n"

    messages = [{"role": "system", "content": intro}]
    messages += history[-5:]
    messages.append({"role": "user", "content": user_message})

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": messages,
                "temperature": 0.8,
            },
        )
        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            reply = result["choices"][0]["message"]["content"]
            if language == "hindi":
                reply = convert_to_transliteration(reply)
            add_to_history(user_id, user_message, reply)
            return jsonify({"reply": reply.strip()})
        else:
            return jsonify({"reply": "I'm sorry, I couldn't understand that response."})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)












