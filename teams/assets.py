import re


def _normalize(name):
    value = (name or "").strip().lower()
    value = re.sub(r"[^\w\s]", " ", value)
    tokens = [token for token in value.split() if token not in {"club"}]
    return " ".join(tokens)


TEAM_LOGO_MAP = {
    "avangar": "teams/logos/avangar.jpg",
    "aktobe": "teams/logos/aktobe.jpg",
    "aktobe rush": "teams/logos/aktobe-rush.jpg",
    "almaty hoopers": "teams/logos/almaty-hoopers.jpg",
    "altay phoenix": "teams/logos/altay-phoenix.jpg",
    "astana": "teams/logos/astana.jpg",
    "bc astana": "teams/logos/bc-astana.jpg",
    "astana falcons": "teams/logos/astana-falcons.jpg",
    "atyrau": "teams/logos/atyrau.jpg",
    "elimai semey": "teams/logos/elimai-semey.jpg",
    "irbis almaty": "teams/logos/irbis-almaty.jpg",
    "jetysu taldykorgan": "teams/logos/jetysu-taldykorgan.jpg",
    "jeńis": "teams/logos/jenis.jpg",
    "jenis": "teams/logos/jenis.jpg",
    "k23": "teams/logos/k23.jpg",
    "kairat almaty": "teams/logos/kairat-almaty.jpg",
    "kairat": "teams/logos/kairat-almaty.jpg",
    "kaisar kyzylorda": "teams/logos/kaisar-kyzylorda.jpg",
    "karaganda eagles": "teams/logos/karaganda-eagles.jpg",
    "kyzylzhar petropavl": "teams/logos/kyzylzhar-petropavl.jpg",
    "nomad fire": "teams/logos/nomad-fire.jpg",
    "okzhetpes kokshetau": "teams/logos/okzhetpes-kokshetau.jpg",
    "ordabasy shymkent": "teams/logos/ordabasy-shymkent.jpg",
    "ordabasy": "teams/logos/ordabasy-shymkent.jpg",
    "qazaq wolves": "teams/logos/qazaq-wolves.jpg",
    "shymkent united": "teams/logos/shymkent-united.jpg",
    "steppe titans": "teams/logos/steppe-titans.jpg",
    "kazakhstan dota 2": "teams/logos/team-kazakhstan-dota2.jpg",
    "tobol": "teams/logos/tobol.jpg",
    "turan": "teams/logos/turan.jpg",
    "ulytau": "teams/logos/ulytau.jpg",
}


TEAM_ALIAS_MAP = {
    "fc astana": "astana",
    "fc kairat": "kairat almaty",
    "fc ordabasy": "ordabasy shymkent",
    "team kazakhstan dota 2": "kazakhstan dota 2",
    "team kazakhstan dota2": "kazakhstan dota 2",
    "k 23": "k23",
}


def resolve_team_logo_asset(team_name):
    normalized = _normalize(team_name)
    canonical = TEAM_ALIAS_MAP.get(normalized, normalized)
    return TEAM_LOGO_MAP.get(canonical)
