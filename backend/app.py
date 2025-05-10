import datetime
from main import AdamAI
from flask import Flask, Response, request, jsonify, send_from_directory, abort
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from threading import Thread
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log the current working directory and paths
logger.info(f"Current working directory: {os.getcwd()}")
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))
logger.info(f"Frontend path: {frontend_path}")
logger.info(f"Static folder exists: {os.path.exists(os.path.join(frontend_path, 'static'))}")
app = Flask(__name__)
CORS(app)
app = Flask(__name__, static_folder='../frontend/static')
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # For development only (lock this down in production)
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept"],
        "supports_credentials": True,
        "max_age": 86400
    }
})

load_dotenv('.env')

adam = AdamAI()

@app.route('/api/chat', methods=['POST','OPTION'])
def handle_chat():
    """Main chat endpoint"""
    logger.info("Incoming request headers: %s", request.headers)
    logger.info("Request method: %s", request.method)
    if request.method == 'OPTIONS':
        response = jsonify({"status": "preflight"})
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response
    
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing required field: message"
            }), 400

        user_id = data.get('user_id', 'anonymous')
        message = data.get('message', '').strip()

        if not message:
            return jsonify({
                "status": "error",
                "message": "Message cannot be empty"
            }), 400

        response = adam.respond(user_id, message)
        
        logger.info(f"User {user_id} asked: {message}")
        logger.info(f"Adam responded: {response[:100]}...")

        return jsonify({
            "status": "success",
            "response": response,
            "user_id": user_id,
            "timestamp": datetime.datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Internal server error",
            "error": str(e)
        }), 500

@app.route('/api/conversation', methods=['GET'])
def get_conversation_history():
    """Get conversation history"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                "status": "error",
                "message": "user_id parameter is required"
            }), 400

        limit = int(request.args.get('limit', 5))
        history = adam.memory.get_recent_conversations(user_id, limit=limit)

        return jsonify({
            "status": "success",
            "history": history,
            "count": len(history)
        }), 200

    except Exception as e:
        logger.error(f"Conversation history error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Could not retrieve conversation history"
        }), 500

@app.route('/api/system/status', methods=['GET'])
def system_status():
    """System health check"""
    return jsonify({
        "status": "operational",
        "version": "1.0",
        "service": "AdamAI",
        "timestamp": datetime.datetime.now().isoformat()
    }), 200

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
    # Build absolute path to static folder
    static_folder = os.path.abspath(
        os.path.join(app.root_path, '../frontend/static')
    )
    
    # Build absolute path to requested file
    file_path = os.path.join(static_folder, filename)
    
    # Security check - prevent directory traversal
    if not os.path.abspath(file_path).startswith(static_folder):
        abort(403)  # Forbidden
    
    # Check if file exists
    if not os.path.isfile(file_path):
        abort(404)  # Not found
    
    # Send the file
    return send_from_directory(static_folder, filename)
    


@app.route('/api/learn', methods=['POST'])
def trigger_learning():
    adam.run_learning_cycle()

@app.route('/api/status/health', methods=['GET'])
def status():
    """System health check"""
    return jsonify({
        "status": "operational",
        "knowledge": "active" if adam.knowledge_base else "degraded",
        "conversations": len(adam.active_conversations)
    })

@app.route('/api/debug', methods=['GET'])
def debug():
    test_response = adam.respond('test_user', 'test question')
    return jsonify({
        "system_status": "operational",
        "test_response": test_response,
        "response_type": str(type(test_response))
    })

    
if __name__ == '__main__':
    port = int(os.getenv("PORT"))
    debug_mode = os.getenv("DEBUG").lower() == "true"
    app.run(host='0.0.0.0', port=port)