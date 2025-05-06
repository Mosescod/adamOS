from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import AdamAI
from typing import Optional

app = FastAPI(
    title="AdamAI Spiritual API",
    description="Digital prophet API with emotional intelligence",
    version="0.1.0"
)

class AdamRequest(BaseModel):
    query: str
    user_id: str = "guest"
    mood_override: Optional[float] = None

class AdamResponse(BaseModel):
    response: str
    detected_theme: str
    mood_score: float

adam_instances = {}  # {user_id: AdamAI}

@app.post("/query", response_model=AdamResponse)
async def ask_adam(request: AdamRequest):
    try:
        # Get or create Adam instance
        if request.user_id not in adam_instances:
            adam_instances[request.user_id] = AdamAI(request.user_id)
        
        adam = adam_instances[request.user_id]
        
        # Mood override for testing
        if request.mood_override:
            adam.emotions.mood = request.mood_override
        
        # Process query
        response = adam.query(request.query)
        
        return {
            "response": response,
            "detected_theme": adam.memory.get_preferred_theme(),
            "mood_score": round(adam.emotions.mood, 2)
        }
    
    except Exception as e:
        raise HTTPException(500, f"Clay cracked: {str(e)}")

@app.get("/users/{user_id}/insights")
async def get_insights(user_id: str):
    if user_id not in adam_instances:
        raise HTTPException(404, "User not found")
    return adam_instances[user_id].get_user_insights()