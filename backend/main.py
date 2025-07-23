from fastapi import FastAPI
from routes.route import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"] for Vite dev server
    allow_credentials=True,
    allow_methods=["*"],  # or ["POST", "GET", "OPTIONS"]
    allow_headers=["*"],  # or ["Content-Type", "Authorization"]
)

app.include_router(router)



