
from flask import Flask, render_template, request, jsonify
from ai_service import generate_response, OLLAMA_MODEL

app = Flask(__name__)


# ==========================================
# 1. HOME PAGE
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# 2. CHAT API
# ==========================================

@app.route("/chat", methods=["POST"])
def chat():

    try:
        data = request.get_json(silent=True) or {}

        user_text = data.get("text", "").strip()

        # Validate user input
        if not user_text:
            return jsonify({
                "error": "Please enter a message."
            }), 400

        if len(user_text) > 3000:
            return jsonify({
                "error": "Your message is too long. Please keep it under 3000 characters."
            }), 400

        # Generate Dzongkha response
        ai_response = generate_response(user_text)

        if not ai_response:
            return jsonify({
                "error": "The AI model returned an empty response."
            }), 502

        return jsonify({
            "original": user_text,
            "response": ai_response,
            "model": OLLAMA_MODEL,
            "translation_model": "KarmaCST NLLB-200",
            "warning": "AI-generated Dzongkha response. Please verify accuracy."
        }), 200

    except Exception:

        app.logger.exception(
            "Error generating Dzongkha response"
        )

        return jsonify({
            "error": "An error occurred while generating the response. Please try again."
        }), 500


# ==========================================
# 3. RUN FLASK APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )
