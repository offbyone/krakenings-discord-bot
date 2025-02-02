from __future__ import annotations

from abc import abstractmethod
from datetime import date, datetime
from io import BytesIO
from typing import List

import httpx
from discord import Color
from PIL import Image
from pydantic import BaseModel, Field, HttpUrl
from pydantic_extra_types.color import Color

from .images import make_vs_image


class Logo(BaseModel):
    href: HttpUrl
    width: int
    height: int
    alt: str
    rel: List[str]


class LeagueSeasonType(BaseModel):
    id: str
    type: int
    name: str
    abbreviation: str


class LeagueSeason(BaseModel):
    year: int
    start_date: datetime | None = Field(alias="startDate")
    end_date: datetime | None = Field(alias="endDate")
    display_name: str | None = Field(alias="displayName")
    type: LeagueSeasonType


class BaseLeague(BaseModel):
    id: int
    uid: str
    name: str
    abbreviation: str
    slug: str


class WrappedTeam(BaseModel):
    team: Team


class League(BaseLeague):
    wrapped_teams: list[WrappedTeam] = Field(alias="teams")


class ScheduleLeague(BaseLeague):
    logos: list[Logo]
    calendar_type: str = Field(alias="calendarType")
    season: LeagueSeason
    calendar_is_whitelist: bool = Field(alias="calendarIsWhitelist")
    calendar_start_date: datetime = Field(alias="calendarStartDate")
    calendar_end_date: datetime = Field(alias="calendarEndDate")
    calendar: list[datetime]


class Day(BaseModel):
    date: date


class Season(BaseModel):
    year: int
    type: int


class EventSeason(Season):
    slug: str


class CompetitionType(BaseModel):
    abbreviation: str


class Venue(BaseModel):
    id: str
    full_name: str = Field(alias="fullName")
    indoor: bool | None = Field(default=None)


class BaseTeam(BaseModel):
    id: str
    uid: str
    abbreviation: str
    location: str
    name: str
    display_name: str = Field(alias="displayName")
    short_display_name: str = Field(alias="shortDisplayName")
    color: Color | None = Field(default=None)
    alternate_color: Color | None = Field(alias="alternateColor", default=None)

    @abstractmethod
    def get_logo_url(self, specifier: list[str] | None = None) -> HttpUrl: ...


class ScheduleTeam(BaseTeam):
    logo: HttpUrl

    def get_logo_url(self, specifier: list[str] | None = None) -> HttpUrl:
        return self.logo


class Team(BaseTeam):
    nickname: str
    slug: str
    logos: list[Logo]

    def get_logo_url(self, specifier: list[str] | None = None) -> HttpUrl:
        if specifier is None:
            return self.logos[0].href

        specifier_str = ".".join(specifier)

        for logo in self.logos:
            if specifier_str == ".".join(logo.rel):
                return logo.href

        return self.logos[0].href


class Competitor(BaseModel):
    id: str
    uid: str
    type: str
    order: int | None
    home_away: str = Field(alias="homeAway")
    team: ScheduleTeam


class Competition(BaseModel):
    id: str
    type: CompetitionType | None = Field(default=None)
    neutral_site: bool = Field(alias="neutralSite", default=False)
    venue: Venue
    competitors: list[Competitor]


class Event(BaseModel):
    id: str
    uid: str
    date: datetime
    name: str
    short_name: str = Field(alias="shortName")
    season: EventSeason
    competitions: list[Competition]


class Schedule(BaseModel):
    leagues: list[ScheduleLeague]
    season: Season
    day: Day
    events: list[Event]


class Sport(BaseModel):
    leagues: list[League]


class TeamsModel(BaseModel):
    sports: list[Sport]

    def get_team(self, team_id: str) -> Team:
        # get a flat least of teams from the sport / league / wrapped team structure:\
        all_teams: dict[str, Team] = {}
        for sport in self.sports:
            for league in sport.leagues:
                for wt in league.wrapped_teams:
                    all_teams[wt.team.abbreviation.lower()] = wt.team
                    all_teams[wt.team.slug.lower()] = wt.team

        return all_teams[team_id]


BASE_URL = "https://site.api.espn.com"


def schedule_for_league(sport: str, league: str) -> Schedule:
    url = f"{BASE_URL}/apis/site/v2/sports/{sport}/{league}/scoreboard"

    response = httpx.get(url)
    response.raise_for_status()

    raw = response.read()
    return Schedule.model_validate_json(raw)


def team_for_league(sport: str, league: str) -> list[Team]:
    url = f"{BASE_URL}/apis/site/v2/sports/{sport}/{league}/teams"

    response = httpx.get(url)
    response.raise_for_status()

    raw = response.read()
    return TeamsModel.model_validate_json(raw).sports[0].leagues[0].teams


def fetch_image(url: HttpUrl) -> Image.Image:
    response = httpx.get(str(url))
    response.raise_for_status()

    return Image.open(BytesIO(response.content)).convert("RGBA")


def vs_image(
    away_team_logo_url: HttpUrl, home_team_logo_url: HttpUrl, dimensions: Dimensions
) -> Image.Image:
    team1_logo, team2_logo = (
        fetch_image(away_team_logo_url),
        fetch_image(home_team_logo_url),
    )

    return make_vs_image(team1_logo, team2_logo, dimensions)
