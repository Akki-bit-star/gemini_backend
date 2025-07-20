from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import auth, user, chatroom, subscription
from app.database import engine, Base
from app.models import user as user_model, chatroom as chatroom_model, message as message_model, otp as otp_model
from fastapi.staticfiles import StaticFiles

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Gemini Backend Clone",
    description="A FastAPI backend system with chatrooms, AI integration, and subscription management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(chatroom.router)
app.include_router(subscription.router)


@app.get("/")
async def root():
    return {"message": "Gemini Backend Clone API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Mount the static directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Global exception handler


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
