from flask import Flask, request, jsonify
from main import AdamAI
from core.knowledge.knowledge_db import KnowledgeDatabase
import logging
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AdamAI without any interactive elements
adam = AdamAI(quran_db=KnowledgeDatabase(), user_id="web_user")

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
    
@app.route('/ping')
def ping():
    return jsonify({"status": "alive", "db_connected": adam.quran_db.is_populated()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)