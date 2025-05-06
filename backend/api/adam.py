from http.server import BaseHTTPRequestHandler
import json
from main import AdamAI
from core.knowledge.mongo_db import MongoDB

# Initialize AdamAI (runs once per deployment)
adam = AdamAI(quran_db=MongoDB(), user_id="vercel_user")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        
        response = adam.query(data.get('question', ''))
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "response": response,
            "status": "success"
        }).encode('utf-8'))