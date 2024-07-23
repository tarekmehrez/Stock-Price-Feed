import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(os.getenv("ENV_PATH", ".")) / ".env"
load_dotenv(dotenv_path=env_path)

RUNNING_TESTS = False
DOCS_PREFIX = os.getenv("DOCS_PREFIX", "")

# REDIS
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_URI = f"redis://{REDIS_HOST}:{REDIS_PORT}"

# partner websocket
SOCKET_HOST = os.getenv("SOCKET_HOST", "localhost")
SOCKET_PORT = os.getenv("SOCKET_PORT", 8080)
SOCKET_URI = f"ws://{SOCKET_HOST}:{SOCKET_PORT}"

# mongodb
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", 27017)


TSDB_NAME = os.getenv("TSDB_NAME", "TRADEREP")
INSTRUMENT_PREFIX = os.getenv("INSTRUMENT_PREFIX", "INSTR")
ENV = os.getenv("ENV", "dev")
