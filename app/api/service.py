import os

from external_sources_service.target_site_worker import RequestWorker
from fastapi import HTTPException
from app.models import PrizeModel

def _get_target_site_worker() -> RequestWorker:
    return RequestWorker(os.getenv('USERNAME'), os.getenv('PASSWORD'))

def _authenticate(target_site_worker: RequestWorker) -> None:
    if not target_site_worker.authenticate():
        raise HTTPException(401)

def get_prizes() -> list[PrizeModel]:
    site_worker = _get_target_site_worker()
    _authenticate(site_worker)
    prizes_dict = site_worker.get_prizes()
    return [PrizeModel(**prize) for prize in prizes_dict]