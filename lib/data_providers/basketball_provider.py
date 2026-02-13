from datetime import datetime, timezone

from .cache import get_cached, set_cached
from .http_utils import fetch_json
from .types import ProviderResult, TeamEntity, TournamentEntity


class BasketballProvider:
    cache_key = "provider:basketball"
    ttl_minutes = 20
    source_url = "https://www.thesportsdb.com/"
    target_team = "BC Astana"

    def fetch(self) -> ProviderResult:
        cached = get_cached(self.cache_key, self.ttl_minutes)
        if cached:
            return cached

        fetched_at = datetime.now(timezone.utc)
        try:
            payload = fetch_json(
                "https://www.thesportsdb.com/api/v1/json/3/searchteams.php",
                params={"t": self.target_team},
            )
            rows = payload.get("teams") or []
            teams = []
            for row in rows:
                if (row.get("strSport") or "").lower() != "basketball":
                    continue
                teams.append(
                    TeamEntity(
                        id=f"basketball-{row.get('idTeam')}",
                        name=row.get("strTeam") or self.target_team,
                        discipline="basketball",
                        country=row.get("strCountry") or "Kazakhstan",
                        city=row.get("strStadiumLocation") or "Astana",
                        logo=row.get("strBadge") or "",
                        source_url=row.get("strWebsite") or self.source_url,
                        updated_at=fetched_at,
                    )
                )

            tournaments = [
                TournamentEntity(
                    id="basketball-kz-main",
                    name="Kazakhstan Basketball Events",
                    discipline="basketball",
                    tier="National/Regional",
                    location="Kazakhstan",
                    status="upcoming",
                    source_url=self.source_url,
                    updated_at=fetched_at,
                )
            ]

            result = ProviderResult(
                teams=teams,
                tournaments=tournaments,
                matches=[],
                is_fallback=False if teams else True,
                fetched_at=fetched_at,
                sources=[self.source_url],
            )
        except Exception:
            result = ProviderResult(
                teams=[],
                tournaments=[],
                matches=[],
                is_fallback=True,
                fetched_at=fetched_at,
                sources=[self.source_url],
            )

        set_cached(self.cache_key, result)
        return result
