from flask import Flask, request, jsonify, send_from_directory
from core.knowledge.quran_db import QuranDatabase
from main import AdamAI
import logging
from pathlib import Path
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='interfaces/web/static')

# Initialize components
def initialize_components():
    try:
        # Database setup
        db_path = Path("core/knowledge/data/quran.db")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        quran_db = QuranDatabase(db_path=str(db_path))
        
        # AI initialization
        adam = AdamAI(quran_db=quran_db, user_id="web_user")
        
        logger.info("Components initialized successfully")
        return adam
        
    except Exception as e:
        logger.critical(f"Initialization failed: {str(e)}")
        raise RuntimeError("System startup failed")

adam = initialize_components()

# API Endpoints
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

@app.route('/api/security', methods=['POST'])
def handle_security():
    try:
        data = request.get_json()
        logger.info(f"Security alert: {data}")
        return jsonify({
            "status": "alert",
            "message": "NOAH-Q protocols activated"
        })
    except Exception as e:
        logger.error(f"Security error: {str(e)}")
        return jsonify({"error": "Security subsystem failure"}), 500

@app.route('/')
def serve_index():
    return send_from_directory('interfaces/web', 'index.html')

# Frontend Routes
@app.route('/homepage')
def home():
    return send_from_directory('interfaces/web', 'index.html')


@app.route('/<page>')
def serve_page(page):
    valid_pages = ['adam', 'docs', 'noahq']
    if page in valid_pages:
        return send_from_directory('interfaces/web/pages', f'{page}.html')
    return "Not Found", 404

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('interfaces/web/static', path)
    

# Health check
@app.route('/health')
def health_check():
    return jsonify({
        "status": "operational",
        "database": "connected" if adam.quran_db.is_populated() else "empty"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)