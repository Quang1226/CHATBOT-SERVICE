from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="VNJ Chatbot Customer Care Service", version="1.0.0")

# Danh sách các domain được phép gọi API
origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://www.vnj-ss.com",
    "https://vnj-ss.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to VNJ Chatbot Service API"}