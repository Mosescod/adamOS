from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from main import AdamAI

app = FastAPI()

# CORS for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Shared Adam instance
adam = AdamAI("api_gateway")

@app.post("/v1/query")
async def unified_api(request: Request):
    data = await request.json()
    platform = request.headers.get("X-Platform")
    
    response = adam.query(
        text=data["message"],
        user_id=data.get("user_id", "anonymous"),
        platform=platform
    )
    
    return {
        "response": response,
        "meta": {
            "mood": adam.emotions.mood,
            "memory_id": adam.memory.current_session
        }
    }