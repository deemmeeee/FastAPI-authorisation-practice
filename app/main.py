from typing import Union
from .config import APP_NAME, APP_VERSION, APP_DESCRIPTION
from fastapi import FastAPI

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
)


@app.get("/status")
def read_status():
    return {"title": APP_NAME,
            "version": APP_VERSION,
            "description": APP_DESCRIPTION}


