# memory_store.py

chat_memory = {}
user_traits = {}

def add_to_history(user_id, user_msg, ai_reply):
    if user_id not in chat_memory:
        chat_memory[user_id] = []
    chat_memory[user_id].append({"role": "user", "content": user_msg})
    chat_memory[user_id].append({"role": "assistant", "content": ai_reply})

def get_last_messages(user_id):
    return chat_memory.get(user_id, [])

def update_traits(user_id, message):
    # This is a basic demo — in real use, you'd do NLP-based personality detection
    traits = user_traits.get(user_id, set())

    if any(word in message.lower() for word in ["tired", "lost", "sad", "alone"]):
        traits.add("emotionally vulnerable")
    if any(word in message.lower() for word in ["why", "how", "what", "meaning"]):
        traits.add("deep thinker")
    if any(word in message.lower() for word in ["angry", "frustrated", "irritated"]):
        traits.add("short-tempered")
    if any(word in message.lower() for word in ["happy", "excited", "grateful"]):
        traits.add("positive")
    
    user_traits[user_id] = traits
    return list(traits)

