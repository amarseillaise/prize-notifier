from pydantic import BaseModel
from typing import  Optional

class PrizeModel(BaseModel):
    id: int
    name: str
    alias: str
    ball: int
    active: bool
    limit: bool
    totalLimit: bool

    def is_available(self) -> bool:
        return not self.totalLimit

class TokenModel(BaseModel):
    access_token: str
    refresh_token: str

class AuthResponseModel(BaseModel):
    status: int
    message: str
    data : Optional[TokenModel] = None