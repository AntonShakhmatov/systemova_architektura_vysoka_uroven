from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

@app.route('/python', methods=['POST'])
def embed():
    data = request.json or {}
    texts = data.get('texts', [])
    python = model.encode(texts, show_progress_bar=False).tolist()
    return jsonify({'python': python})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
