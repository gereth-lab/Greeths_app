from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from dotenv import load_dotenv
from app.database import engine, Base, get_db
from app.routers import auth, posts, comments, messages, users, media
from app.models import User, Post, Comment, Message, Reaction
from app.config import settings
from app.websocket import manager
import json

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Greeths API",
    description="Advanced Social Media Platform with Real-time Features",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_FOLDER), name="uploads")

# Routes
app.include_router(auth.router, tags=["Authentication"])
app.include_router(posts.router, tags=["Posts"])
app.include_router(comments.router, tags=["Comments"])
app.include_router(messages.router, tags=["Messages"])
app.include_router(users.router, tags=["Users"])
app.include_router(media.router, tags=["Media"])

@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "Welcome to Greeths API v2.0",
        "version": "2.0.0",
        "features": [
            "Posts with media (image, video, voice)",
            "Comments with reactions",
            "Real-time messaging",
            "User profiles & following",
            "WebSocket support",
            "Advanced authentication"
        ],
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "Greeths API"}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """WebSocket endpoint for real-time messaging and notifications"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "message":
                recipient_id = message_data.get("recipient_id")
                await manager.send_personal_message(
                    f"New message from {user_id}",
                    recipient_id
                )
            elif message_data.get("type") == "typing":
                recipient_id = message_data.get("recipient_id")
                await manager.send_personal_message(
                    json.dumps({"type": "typing", "user_id": user_id}),
                    recipient_id
                )
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="info")
