from fastapi import APIRouter
from app.api.v1.endpoints import chat, faq, auth

api_router = APIRouter()

api_router.include_router(chat.router, prefix="/chat", tags=["Chatbot Public"])
api_router.include_router(faq.router, prefix="/faq", tags=["Admin FAQ Management"])
api_router.include_router(auth.router, prefix="/auth", tags=["Admin Authentication"])