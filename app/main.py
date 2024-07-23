import logging
import asyncio

import fastapi_plugins
from fastapi import FastAPI
from fastapi import status
from prometheus_fastapi_instrumentator import Instrumentator

from app import routers
from app import consumers
from app import settings
from app.providers import RedisConnection


class AppSettings(fastapi_plugins.RedisSettings):
    api_name: str = str(__name__)


app = FastAPI(
    title="Instruments Feed Service", version="1.0.0", root_path=settings.DOCS_PREFIX,
)
instrumentator = Instrumentator().instrument(app).expose(app)
instrumentator.expose(app, include_in_schema=False, should_gzip=True)

config = AppSettings()


@app.on_event("startup")
async def startup():
    await fastapi_plugins.redis_plugin.init_app(app, config=config)
    await fastapi_plugins.redis_plugin.init()
    logging.info("Created new redis connection.")

    # dont run socket listeners when tests are running
    if not settings.RUNNING_TESTS:
        asyncio.create_task(consumers.consume_instruments())
        asyncio.create_task(consumers.consume_ticks())


@app.on_event("shutdown")
async def shutdown():
    await fastapi_plugins.redis_plugin.terminate()
    logging.info("Destroyed redis dependency connection.")
    await RedisConnection.close_connection()
    logging.info("Destroyed redis connection.")


@app.get("/healthz", status_code=status.HTTP_200_OK, tags=["status"])
def health():
    logging.info("Health check")


app.include_router(routers.instruments, prefix="/instruments", tags=["instruments"])
