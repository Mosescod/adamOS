from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from threading import Thread
import time

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
load_dotenv()

class AdamAI:
    def __init__(self):
        self.knowledge_base = self._initialize_knowledge()
        self.active_conversations = {}
        self._start_background_learning()

    def _initialize_knowledge(self):
        """Initialize with multiple fallback layers"""
        try:
            # Primary initialization
            try:
                logger.info("Loading full knowledge base...")
                return self._load_knowledge_db()
            except Exception as e:
                logger.warning(f"Primary init failed: {e}")
                logger.info("Loading minimal knowledge...")
                return self._load_minimal_knowledge()
        except Exception as e:
            logger.critical(f"Knowledge init failed: {e}")
            raise RuntimeError("Knowledge system unavailable")

    def _load_knowledge_db(self):
        """Connect to primary knowledge source"""
        # Implementation would connect to your database
        return {"status": "full_knowledge_loaded"}

    def _load_minimal_knowledge(self):
        """Fallback knowledge"""
        return {
            "themes": ["wisdom", "compassion", "ethics"],
            "fallback": True
        }

    def _start_background_learning(self):
        """Continuous learning thread"""
        def learning_loop():
            while True:
                self._analyze_conversations()
                time.sleep(3600)  # Hourly analysis
        
        Thread(target=learning_loop, daemon=True).start()

    def respond(self, user_id, message):
        """Generate response with context"""
        context = self.active_conversations.get(user_id, {})
        
        # Generate response (simplified)
        response = {
            "response": f"*shapes clay* Regarding {message[:20]}...",
            "context_id": str(hash(f"{user_id}{time.time()}"))
        }
        
        # Update conversation context
        self._update_conversation(user_id, message, response)
        return response

    def _update_conversation(self, user_id, message, response):
        """Maintain conversation state"""
        if user_id not in self.active_conversations:
            self.active_conversations[user_id] = {
                "history": [],
                "themes": []
            }
        
        self.active_conversations[user_id]["history"].append({
            "message": message,
            "response": response,
            "timestamp": time.time()
        })

    def _analyze_conversations(self):
        """Background learning process"""
        logger.info("Running background analysis...")
        # Implementation would analyze recent conversations
        # and update knowledge themes

# Initialize Adam
adam = AdamAI()

# API Endpoints
@app.route('/api/chat', methods=['POST'])
def chat():
    """Main conversation endpoint"""
    data = request.json
    try:
        response = adam.respond(
            user_id=data['user_id'],
            message=data['message']
        )
        return jsonify(response)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"error": "Conversation failed"}), 500

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

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    response = adam.respond(
        user_id=data.get('user_id', 'anonymous'),
        message=data['message']
    )
    return jsonify({"response": response})

@app.route('/api/learn', methods=['POST'])
def trigger_learning():
    adam.run_learning_cycle()

@app.route('/api/status', methods=['GET'])
def status():
    """System health check"""
    return jsonify({
        "status": "operational",
        "knowledge": "active" if adam.knowledge_base else "degraded",
        "conversations": len(adam.active_conversations)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)