import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai

from backend.routes import (
    health_routes, market_overview_routes, comparative_analysis_routes,
    role_details_routes, recent_trends_routes, skill_gap_routes, ask_ai_routes
)

load_dotenv()
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "https://intern-iq-five.vercel.app"
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key=os.getenv("GEMINI_API"), transport="rest")

# API routers

app.include_router(health_routes.router, prefix="/api")
app.include_router(market_overview_routes.router, prefix="/api")
app.include_router(comparative_analysis_routes.router, prefix="/api")
app.include_router(role_details_routes.router, prefix="/api")
app.include_router(recent_trends_routes.router, prefix="/api")
app.include_router(skill_gap_routes.router, prefix="/api")
app.include_router(ask_ai_routes.router, prefix="/api")
