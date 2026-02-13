from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class TeamEntity:
    id: str
    name: str
    discipline: str
    country: str
    city: str = ""
    logo: str = ""
    roster: list[str] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)
    source_url: str = ""
    updated_at: datetime | None = None


@dataclass
class TournamentEntity:
    id: str
    name: str
    discipline: str
    tier: str = ""
    location: str = ""
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: str = "upcoming"
    source_url: str = ""
    updated_at: datetime | None = None


@dataclass
class MatchEntity:
    id: str
    discipline: str
    tournament_id: str
    team_a: str
    team_b: str
    start_time: datetime
    status: str
    score: str = ""
    stream_url: str = ""
    source_url: str = ""
    updated_at: datetime | None = None


@dataclass
class ProviderResult:
    teams: list[TeamEntity]
    tournaments: list[TournamentEntity]
    matches: list[MatchEntity]
    is_fallback: bool
    fetched_at: datetime
    sources: list[str] = field(default_factory=list)
