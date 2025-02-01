from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from io import BytesIO
from typing import List

import httpx
from discord import Color
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel, Field, HttpUrl, TypeAdapter
from pydantic_extra_types.color import Color


@dataclass
class Dimensions:
    width: int
    height: int


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
    teams: list[WrappedTeam]


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
    location: str
    name: str
    display_name: str = Field(alias="displayName")
    short_display_name: str = Field(alias="shortDisplayName")
    color: Color | None = Field(default=None)
    alternate_color: Color | None = Field(alias="alternateColor", default=None)


class ScheduleTeam(BaseTeam):
    logo: HttpUrl


class Team(BaseTeam):
    logos: list[Logo]


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


BASE_URL = "https://site.api.espn.com"


async def schedule_for_league(sport: str, league: str) -> Schedule:
    url = f"{BASE_URL}/apis/site/v2/sports/{sport}/{league}/scoreboard"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

    raw = response.read()
    return Schedule.model_validate_json(raw)


async def team_for_league(sport: str, league: str) -> list[Team]:
    url = f"{BASE_URL}/apis/site/v2/sports/{sport}/{league}/teams"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

    raw = response.read()
    return TeamsModel.model_validate_json(raw).sports[0].leagues[0].teams


async def fetch_image(url: HttpUrl) -> Image.Image:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

    return Image.open(BytesIO(response.read())).convert("RGBA")


async def vs_image(
    away_team_logo_url: HttpUrl, home_team_logo_url: HttpUrl, dimensions: Dimensions
) -> Image.Image:
    team1_logo, team2_logo = await asyncio.gather(
        fetch_image(away_team_logo_url), fetch_image(home_team_logo_url)
    )

    # Resize team logos to fit half of the output width
    output_width, output_height = dimensions.width, dimensions.height
    resize_width = output_width // 2
    resize_height = output_height
    team1_logo = team1_logo.resize((resize_width, resize_height), Image.LANCZOS)
    team2_logo = team2_logo.resize((resize_width, resize_height), Image.LANCZOS)

    # Create output canvas
    out_image = Image.new("RGBA", (output_width, output_height), (255, 255, 255, 255))

    # Paste team logos side by side
    out_image.paste(team1_logo, (0, 0), team1_logo)
    out_image.paste(team2_logo, (resize_width, 0), team2_logo)

    # Add "vs" text in the center
    draw = ImageDraw.Draw(out_image)
    font_size = output_height // 5
    try:
        # Use a simple font bundled with Pillow
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        # Fallback if the font is unavailable
        font = ImageFont.load_default()

    text = "vs"
    text_width, text_height = draw.textsize(text, font=font)
    text_x = (output_width - text_width) // 2
    text_y = (output_height - text_height) // 2

    draw.text((text_x, text_y), text, fill="black", font=font)

    return out_image
