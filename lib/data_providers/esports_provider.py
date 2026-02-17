from datetime import datetime, timezone
from typing import List
from urllib.parse import quote

from .cache import get_cached, set_cached
from .http_utils import fetch_json
from .types import ProviderResult, TeamEntity, TournamentEntity


class EsportsProvider:
    cache_key = "provider:esports"
    ttl_minutes = 20
    liq_cs_api = "https://liquipedia.net/counterstrike/api.php"
    liq_dota_api = "https://liquipedia.net/dota2/api.php"
    liq_pubg_api = "https://liquipedia.net/pubg/api.php"

    tracked_pages = [
        ("cs2", "AVANGAR", "https://liquipedia.net/counterstrike/AVANGAR"),
        ("cs2", "K23", "https://liquipedia.net/counterstrike/K23"),
        ("dota2", "Kazakhstan", "https://liquipedia.net/dota2/Kazakhstan"),
        ("pubg", "Kazakhstan", "https://liquipedia.net/pubg/Kazakhstan"),
    ]

    tracked_tournaments = [
        ("cs2", "PGL Major", "https://liquipedia.net/counterstrike/PGL"),
        ("dota2", "DreamLeague", "https://liquipedia.net/dota2/DreamLeague"),
        ("pubg", "PUBG Continental Series", "https://liquipedia.net/pubg/PUBG_Continental_Series"),
    ]

    def _page_exists(self, api_url: str, query: str):
        payload = fetch_json(
            api_url,
            params={"action": "opensearch", "search": query, "format": "json", "limit": "1"},
            user_agent="KZArenaData/1.0 (liquipedia consumer)",
        )
        items = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        return bool(items)

    def fetch(self) -> ProviderResult:
        cached = get_cached(self.cache_key, self.ttl_minutes)
        if cached:
            return cached

        fetched_at = datetime.now(timezone.utc)
        teams: List[TeamEntity] = []
        tournaments: List[TournamentEntity] = []

        try:
            for discipline, query, url in self.tracked_pages:
                api = self.liq_cs_api if discipline == "cs2" else self.liq_dota_api if discipline == "dota2" else self.liq_pubg_api
                if self._page_exists(api, query):
                    teams.append(
                        TeamEntity(
                            id=f"{discipline}-{quote(query.lower())}",
                            name=query if discipline != "dota2" else "Team Kazakhstan (Dota 2)",
                            discipline=discipline,
                            country="Kazakhstan",
                            source_url=url,
                            updated_at=fetched_at,
                        )
                    )

            for discipline, title, url in self.tracked_tournaments:
                api = self.liq_cs_api if discipline == "cs2" else self.liq_dota_api if discipline == "dota2" else self.liq_pubg_api
                if self._page_exists(api, title):
                    tournaments.append(
                        TournamentEntity(
                            id=f"{discipline}-{quote(title.lower())}",
                            name=title,
                            discipline=discipline,
                            status="upcoming",
                            source_url=url,
                            updated_at=fetched_at,
                        )
                    )

            result = ProviderResult(
                teams=teams,
                tournaments=tournaments,
                matches=[],
                is_fallback=False if teams else True,
                fetched_at=fetched_at,
                sources=[
                    "https://liquipedia.net/counterstrike/Main_Page",
                    "https://liquipedia.net/dota2/Main_Page",
                    "https://liquipedia.net/pubg/Main_Page",
                ],
            )
        except Exception:
            result = ProviderResult(
                teams=[],
                tournaments=[],
                matches=[],
                is_fallback=True,
                fetched_at=fetched_at,
                sources=[
                    "https://liquipedia.net/counterstrike/Main_Page",
                    "https://liquipedia.net/dota2/Main_Page",
                    "https://liquipedia.net/pubg/Main_Page",
                ],
            )

        set_cached(self.cache_key, result)
        return result
