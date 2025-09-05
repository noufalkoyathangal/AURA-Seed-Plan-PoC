from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title="AURA Seed Plan PoC",
    version="0.1.0",
    description=(
        "Seed Plan vertical slice: validate data, cluster stores (K-Means + silhouette), "
        "generate draft assortment under constraints, validate, and export. "
        "Includes LangGraph workflow endpoint."
    ),
    swagger_ui_parameters=settings.swagger_ui_parameters,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}
