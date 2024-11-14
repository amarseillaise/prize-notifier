import os

import uvicorn
from fastapi import FastAPI, status

from app.api import service
from app.models import PrizeModel

server = ...
app = FastAPI()

def run_uvicorn():
    global server
    config = {
        'app': app,
        'host': os.getenv('HOST'),
        'port': int(os.getenv('PORT')),
        'reload': True,
    }
    server = uvicorn.Server(uvicorn.Config(**config))
    server.run()

@app.get("/api/prizes/",
         response_description='Returns a list of all prizes',
         response_model=list[PrizeModel],
         status_code=status.HTTP_200_OK)
def get_prizes() -> list[PrizeModel]:
    prizes = service.get_prizes()
    return prizes