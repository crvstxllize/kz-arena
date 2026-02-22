from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, List, Dict


@dataclass
class TeamEntity:
    id: str
    name: str
    discipline: str
    country: str
    city: str = ""
    logo: str = ""
    roster: List[str] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)
    source_url: str = ""
    updated_at: Optional[datetime] = None


@dataclass
class TournamentEntity:
    id: str
    name: str
    discipline: str
    tier: str = ""
    location: str = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str = "upcoming"
    source_url: str = ""
    updated_at: Optional[datetime] = None


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
    updated_at: Optional[datetime] = None


@dataclass
class ProviderResult:
    teams: List[TeamEntity]
    tournaments: List[TournamentEntity]
    matches: List[MatchEntity]
    is_fallback: bool
    fetched_at: datetime
    sources: List[str] = field(default_factory=list)