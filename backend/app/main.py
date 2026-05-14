from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analysis import router as analysis_router
from app.api.routes.image import router as image_router
from app.api.routes.project import router as project_router
from app.core.config import settings
from app.core.database import Base, engine, run_migrations

Base.metadata.create_all(bind=engine)
run_migrations()

app = FastAPI(title="纹生万象 Backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_origin_regex=settings.cors_allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(analysis_router)
app.include_router(image_router)
app.include_router(project_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
