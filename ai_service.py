
import requests
import torch
import time

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


# ==========================================
# MODEL CONFIGURATION
# ==========================================

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:1.5b"

TRANSLATION_MODEL = "KarmaCST/nllb-200-distilled-600M-en-to-dz"

torch.set_num_threads(4)


# ==========================================
# LOAD DZONGKHA TRANSLATION MODEL
# ==========================================

print("Loading Dzongkha translation model...")

tokenizer = AutoTokenizer.from_pretrained(
    TRANSLATION_MODEL,
    src_lang="eng_Latn"
)

translator = AutoModelForSeq2SeqLM.from_pretrained(
    TRANSLATION_MODEL
)

translator.eval()
translator.generation_config.max_length = None

print("Dzongkha translation model ready!")


# ==========================================
# GENERATE ENGLISH RESPONSE USING QWEN
# ==========================================

def generate_english_response(user_text):

    system_prompt = """
You are a helpful, friendly, general-purpose AI assistant.

Understand the user's intention and provide a useful,
accurate and natural response.

LANGUAGE RULES:
1. Write entirely in clear English.
2. Never attempt to write in Dzongkha.
3. Use simple, natural and grammatically correct sentences.
4. Avoid complicated vocabulary, idioms and slang.
5. Use short sentences with one main idea whenever possible.
6. Preserve names, dates, numbers and important details.

RESPONSE GUIDELINES:
- For greetings, respond naturally and briefly.
- For general questions, answer directly.
- For explanations, organize information clearly.
- For educational questions, explain concepts simply.
- For stories, create a coherent story with a beginning,
  middle and ending.
- For advice, provide practical suggestions.
- Use bullet points only when helpful.
- Avoid unnecessary introductions and conclusions.
- Give enough information to answer the request.

Your response will be translated into Dzongkha by another
AI model. Prioritize clarity, meaning and simple sentence
structure.
"""

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_text
            }
        ],
        "stream": False,
        "keep_alive": "10m",
        "options": {
            "temperature": 0.3,
            "num_predict": 180,
            "num_ctx": 1024,
            "num_thread": 4
        }
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=180
    )

    response.raise_for_status()

    english_response = response.json()["message"]["content"].strip()

    if not english_response:
        raise ValueError("Ollama returned an empty response.")

    return english_response


# ==========================================
# TRANSLATE ENGLISH INTO DZONGKHA
# ==========================================

def translate_to_dzongkha(english_text):

    inputs = tokenizer(
        english_text,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    with torch.inference_mode():

        translated_tokens = translator.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(
                "dzo_Tibt"
            ),
            max_new_tokens=256,
            num_beams=4,
            early_stopping=True,
            length_penalty=1.0
        )

    result = tokenizer.batch_decode(
        translated_tokens,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False
    )

    dzongkha_response = result[0].strip()

    if not dzongkha_response:
        raise ValueError("The translation model returned an empty response.")

    return dzongkha_response


# ==========================================
# COMPLETE DZONGKHA AI RESPONSE
# ==========================================

def generate_response(user_text):

    start_time = time.perf_counter()

    # Generate English response
    english_response = generate_english_response(user_text)

    ollama_end = time.perf_counter()

    # Translate English response into Dzongkha
    dzongkha_response = translate_to_dzongkha(english_response)

    translation_end = time.perf_counter()

    # Performance report
    print("\n========== PERFORMANCE REPORT ==========")
    print(f"Qwen generation: {ollama_end - start_time:.2f} seconds")
    print(f"Dzongkha translation: {translation_end - ollama_end:.2f} seconds")
    print(f"Total processing: {translation_end - start_time:.2f} seconds")
    print("========================================\n")

    return dzongkha_response
