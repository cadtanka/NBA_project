from pydantic import BaseModel
from typing import List

class GameMetaData(BaseModel):
    game_id: int
    status: str
    teams: List[str]
    date: str