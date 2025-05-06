from flask import Flask, request, jsonify
from main import AdamAI
from core.knowledge.mongo_db import MongoDB  # or QuranDatabase
import logging
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AdamAI without any interactive elements
adam = AdamAI(quran_db=MongoDB(), user_id=os.getenv("USER_ID", "web_user"))

@app.route('/api/query', methods=['POST'])
def handle_query():
    try:
        data = request.get_json()
        question = data.get('question', '')
        response = adam.query(question)
        return jsonify({
            "response": response,
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)