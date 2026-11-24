import os
import re
import difflib
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

SUPABASE_URL = "https://plvzhecbijalkhcfoeeb.supabase.co"
SUPABASE_KEY = "sb_publishable_k9tGyfnO_ruKyznIsSj0kQ_EVMpHzkb"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def match_case(original: str, suggestion: str) -> str:
    if original.isupper():
        return suggestion.upper()
    if original and original[0].isupper():
        return suggestion.capitalize()
    return suggestion


def get_suggestions(word_lower: str, original_word: str) -> list:
    if not word_lower:
        return []
    first_char = word_lower[0]
    res = (
        supabase.table("words")
        .select("word")
        .ilike("word", f"{first_char}%")
        .limit(1000)
        .execute()
    )
    candidates = list({row["word"].strip().lower() for row in (res.data or []) if row.get("word")})
    matches = difflib.get_close_matches(word_lower, candidates, n=5, cutoff=0.55)
    return [match_case(original_word, m) for m in matches]


@app.route("/", methods=["GET"])
def home():
    res = supabase.table("words").select("word").limit(1).execute()
    return jsonify({
        "status": "SózSheber API islep tur!",
        "words_readable": len(res.data or []) > 0
    })


@app.route("/api/check", methods=["POST"])
def check_text():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"errors": []})

    raw_words = re.findall(r"[^\W\d_]+(?:[ʻ’ʼ'`][^\W\d_]+)*", text)
    unique_lower = list({w.lower() for w in raw_words})

    if not unique_lower:
        return jsonify({"errors": []})

    # Bazadan kichik, bosh harfi katta va to'liq katta variantlarni tekshirish
    search_variants = set()
    for w in unique_lower:
        search_variants.add(w)
        search_variants.add(w.capitalize())
        search_variants.add(w.upper())

    response = (
        supabase.table("words")
        .select("word")
        .in_("word", list(search_variants))
        .execute()
    )
    valid_words = {row["word"].strip().lower() for row in (response.data or []) if row.get("word")}

    errors = []
    seen_errors = set()
    for w in raw_words:
        w_lower = w.lower()
        if w_lower not in valid_words and w_lower not in seen_errors:
            seen_errors.add(w_lower)
            errors.append({
                "original": w,
                "suggestions": get_suggestions(w_lower, w)
            })

    return jsonify({"errors": errors})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
