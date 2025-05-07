from flask import Flask, request, jsonify, send_from_directory
from main import AdamAI
from core.knowledge.quran_db import QuranDatabase
import logging
import os
from flask_cors import CORS
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

adam = AdamAI

app = Flask(__name__, static_folder='../frontend/static')
CORS(app)

def initialize_components():
    """Initialize with multiple fallback layers"""
    print("Database status:", adam.quran_db.is_populated() if hasattr(adam, 'quran_db') else "NO DATABASE")
    try:
        user_id = os.getenv("USER_ID", "default_user")
        
        # Primary initialization
        try:
            logger.info("Attempting primary initialization...")
            db = QuranDatabase()
            return AdamAI(quran_db=db, user_id=user_id)
        except Exception as primary_error:
            logger.error(f"Primary init failed: {str(primary_error)}")
            
            # Fallback to minimal initialization
            try:
                logger.info("Attempting minimal initialization...")
                return AdamAI(quran_db=None, user_id=user_id)
            except Exception as fallback_error:
                logger.critical(f"Complete init failure: {str(fallback_error)}")
                raise RuntimeError("Could not create AdamAI instance") from fallback_error
                
    except Exception as e:
        logger.critical(f"System initialization failed: {str(e)}")
        raise RuntimeError("Failed to initialize system") from e

try:
    logger.info("Starting system initialization...")
    adam = initialize_components()
    logger.info("System initialized successfully")
except Exception as e:
    logger.critical(f"Fatal initialization error: {str(e)}")
    raise SystemExit("Could not start application")

@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

# Frontend Routes
@app.route('/homepage')
def home():
    return send_from_directory('../frontend', 'index.html')


@app.route('/<page>')
def serve_page(page):
    valid_pages = ['adam', 'docs', 'noahq']
    if page in valid_pages:
        return send_from_directory('../frontend/pages', f'{page}.html')
    return "Not Found", 404

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(
        os.path.join(app.root_path, '../frontend/static'),
        filename)

@app.route('/api/query', methods=['POST'])
def handle_query():
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                "response": "*molds clay* Speak, that I may hear your words..."
            })
            
        response = adam.query(question)
        return jsonify({"response": response})
        
    except Exception as e:
        logger.error(f"API query failed: {str(e)}")
        return jsonify({
            "response": "*crumbles clay* My connection to sacred knowledge falters..."
        }), 200

@app.route('/health')
def health_check():
    try:
        return jsonify({
            "status": "operational",
            "database": "connected" if adam.quran_db.is_populated() else "empty"
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({"status": "degraded"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)