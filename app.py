import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

# Supabase ulanıwı
SUPABASE_URL = "https://plvzhecbijalkhcfoeeb.supabase.co"
SUPABASE_KEY = "sb_publishable_k9tGyfnO_ruKyznIsSj0kQ_EVMpHzkb"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "SózSheber API islep tur!"})


@app.route('/api/check', methods=['POST'])
def check_text():
    data = request.get_json(silent=True) or {}
    text = data.get('text', '').strip()

    if not text:
        return jsonify({"errors": []})

    # Matndan barcha so'zlarni ajratib olish (qoraqalpoqcha harflar va apostroflar bilan)
    raw_words = re.findall(r"[^\W\d_]+(?:[ʻ’ʼ'`][^\W\d_]+)*", text)
    unique_lower_words = list({w.lower() for w in raw_words})

    if not unique_lower_words:
        return jsonify({"errors": []})

    # Supabase bazasidan barcha so'zlarni tekshirish
    response = supabase.table('words').select('word').in_('word', unique_lower_words).execute()
    valid_words = {row['word'].lower() for row in (response.data or [])}

    # Bazada topilmagan (xato) so'zlarni yig'ish
    errors = []
    seen_errors = set()
    for w in raw_words:
        w_lower = w.lower()
        if w_lower not in valid_words and w_lower not in seen_errors:
            seen_errors.add(w_lower)
            errors.append({
                "original": w,
                "suggestions": []
            })

    return jsonify({"errors": errors})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
