from fastapi import FastAPI

from app.api.v1 import user, job
from app.core.config import config
from app.db.schema import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION)

app.include_router(user.router, prefix="/api/v1")
app.include_router(job.router, prefix="/api/v1")