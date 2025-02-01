from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel


@dataclass
class GameEvent:
    home_team: str
    away_team: str
    time: datetime


@dataclass
class NHLEvent(GameEvent): ...


@dataclass
class NFLEvent(GameEvent): ...


@dataclass
class MLSEvent(GameEvent): ...


# for now I'll do it all in here
class NHLTeamSchedule(BaseModel): ...
