import re
from html import unescape
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from teams.models import Player, Team

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/133.0.0.0 Safari/537.36"
)

ASTANA_OFFICIAL_PLAYERS_URL = "https://fcastana.kz/en/players"
ASTANA_TRANSFERMARKT_SQUAD_URL = "https://www.transfermarkt.com/fc-astana/kader/verein/37856"
ASTANA_COACH_ARTICLE_URL = "https://fcastana.kz/en/news/grigory-babayan-glavnyj-trener-astany"
ASTANA_TRANSFERMARKT_STAFF_URL = "https://www.transfermarkt.com/fc-astana/mitarbeiter/verein/37856"
ASTANA_COACH_FALLBACK_NAME = "Grigorii Babayan"

KAIRAT_TRANSFERMARKT_SQUAD_URL = "https://www.transfermarkt.com/kairat-almaty/kader/verein/10482"
KAIRAT_TRANSFERMARKT_STAFF_URL = "https://www.transfermarkt.com/kairat-almaty/mitarbeiter/verein/10482"
KAIRAT_COACH_FALLBACK_NAME = "Rafael Urazbakhtin"

PLACEHOLDER_NAMES = {f"Игрок {index}" for index in range(1, 31)}
POSITION_KEYWORDS = (
    "Goalkeeper",
    "Sweeper",
    "Centre-Back",
    "Center-Back",
    "Left-Back",
    "Right-Back",
    "Defender",
    "Defensive Midfield",
    "Central Midfield",
    "Attacking Midfield",
    "Midfield",
    "Midfielder",
    "Left Winger",
    "Right Winger",
    "Second Striker",
    "Centre-Forward",
    "Center-Forward",
    "Forward",
    "Striker",
    "Keeper",
    "GK",
    "DF",
    "MF",
    "FW",
)
COACH_ROLE_KEYWORDS = ("manager", "head coach", "coach", "main coach", "trainer")

POSITION_TRANSLATIONS = {
    "goalkeeper": "Вратарь",
    "keeper": "Вратарь",
    "gk": "Вратарь",
    "centre-back": "Защитник",
    "center-back": "Защитник",
    "left-back": "Защитник",
    "right-back": "Защитник",
    "defender": "Защитник",
    "df": "Защитник",
    "sweeper": "Защитник",
    "defensive midfield": "Полузащитник",
    "central midfield": "Полузащитник",
    "attacking midfield": "Полузащитник",
    "midfield": "Полузащитник",
    "midfielder": "Полузащитник",
    "mf": "Полузащитник",
    "left winger": "Нападающий",
    "right winger": "Нападающий",
    "second striker": "Нападающий",
    "centre-forward": "Нападающий",
    "center-forward": "Нападающий",
    "forward": "Нападающий",
    "striker": "Нападающий",
    "fw": "Нападающий",
    "head coach": "Главный тренер",
}

PLAYER_NAME_TRANSLATIONS = {
    "Кайрат": {
        "Temirlan Anarbekov": "Темирлан Анарбеков",
        "Sherkhan Kalmurza": "Шерхан Калмурза",
        "Damir Kasabulat": "Дамир Касабулат",
        "Lucas Áfrico": "Лукас Африко",
        "Aleksandr Martynovich": "Александр Мартынович",
        "Aleksandr Shirobokov": "Александр Широбоков",
        "Luís Mata": "Луиш Мата",
        "Lev Kurgin": "Лев Кургин",
        "Daniyar Tashpulatov": "Данияр Ташпулатов",
        "Aleksandr Mrynskiy": "Александр Мрынский",
        "Erkin Tapalov": "Еркин Тапалов",
        "Dan Glazer": "Дан Глазер",
        "Adilet Sadybekov": "Адилет Садыбеков",
        "Olzhas Baybek": "Олжас Байбек",
        "Jaakko Oksanen": "Яакко Оксанен",
        "Azamat Tuyakbaev": "Азамат Туякбаев",
        "Sebastián Zeballos": "Себастьян Себальос",
        "Ismail Bekbolat": "Исмаил Бекболат",
        "Dastan Satpaev": "Дастан Сатпаев",
        "Jorginho": "Жоржиньо",
        "Ricardinho": "Рикардиньо",
        "Edmilson": "Эдмилсон",
        "Ramazan Bagdat": "Рамазан Багдат",
        "Mansur Birkurmanov": "Мансур Биркурманов",
        "Mukhamedali Abish": "Мухамедали Абиш",
        "Oiva Jukkola": "Ойва Юккола",
        "Rafael Urazbakhtin": "Рафаэль Уразбахтин",
    },
    "Астана": {
        "Abzal Beisebekov": "Абзал Бейсебеков",
        "Afryd Maks Ebonh Nhome": "Африд Макс Эбонг Нхоме",
        "Marin Tomasov": "Марин Томасов",
        "Stanislav Basmanov": "Станислав Басманов",
        "Grigorii Babayan": "Григорий Бабаян",
        "Grigoriy Babayam": "Григорий Бабаян",
        "Agon Haxhija": "Агон Хаджия",
        "Altin Bixhaku": "Алтин Биджаку",
        "Andronit Hasani": "Андронит Хасани",
        "Arnis Mustafa": "Арнис Мустафа",
        "Besnik Shala": "Бесник Шала",
        "Endrit Aliaj": "Эндрит Алиай",
        "Enes Bunjaku": "Энес Буньяку",
        "Genti Shehi": "Генти Шехи",
        "Ivan Bogdanovic": "Иван Богданович",
        "Liburn Zhara": "Либурн Жара",
        "Muharrem Abazi": "Мухаррем Абази",
        "Nahuel Pallas": "Науэль Паллас",
        "Nikola Stanic": "Никола Станич",
        "Qendrim Aliti": "Кендрим Алити",
        "Rohat Nur": "Рохат Нур",
        "Uran Veselji": "Уран Весели",
    },
}

PLAYER_POSITION_OVERRIDES = {
    "Кайрат": {
        "Temirlan Anarbekov": "Вратарь",
        "Sherkhan Kalmurza": "Вратарь",
        "Damir Kasabulat": "Защитник",
        "Lucas Áfrico": "Защитник",
        "Aleksandr Martynovich": "Защитник",
        "Aleksandr Shirobokov": "Защитник",
        "Luís Mata": "Защитник",
        "Lev Kurgin": "Защитник",
        "Daniyar Tashpulatov": "Защитник",
        "Aleksandr Mrynskiy": "Защитник",
        "Erkin Tapalov": "Защитник",
        "Dan Glazer": "Полузащитник",
        "Adilet Sadybekov": "Полузащитник",
        "Olzhas Baybek": "Полузащитник",
        "Jaakko Oksanen": "Полузащитник",
        "Azamat Tuyakbaev": "Полузащитник",
        "Sebastián Zeballos": "Нападающий",
        "Ismail Bekbolat": "Нападающий",
        "Dastan Satpaev": "Нападающий",
        "Jorginho": "Нападающий",
        "Ricardinho": "Нападающий",
        "Edmilson": "Нападающий",
        "Ramazan Bagdat": "Нападающий",
        "Rafael Urazbakhtin": "Главный тренер",
    },
    "Астана": {
        "Abzal Beisebekov": "Защитник",
        "Afryd Maks Ebonh Nhome": "Полузащитник",
        "Marin Tomasov": "Полузащитник",
        "Stanislav Basmanov": "Нападающий",
        "Grigorii Babayan": "Главный тренер",
        "Grigoriy Babayam": "Главный тренер",
    },
}


def fetch_html(url):
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urlopen(request, timeout=20) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def strip_tags(value):
    return re.sub(r"<[^>]+>", " ", value or "")


def clean_text(value):
    return re.sub(r"\s+", " ", unescape(strip_tags(value or ""))).strip()


def extract_title(html):
    match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    return clean_text(match.group(1)) if match else ""


def parse_position_from_text(text):
    lowered = (text or "").lower()
    for position in POSITION_KEYWORDS:
        if position.lower() in lowered:
            return position
    return ""


def localize_player_name(team_name, source_name):
    source_name = (source_name or "").strip()
    if not source_name:
        return ""
    return PLAYER_NAME_TRANSLATIONS.get(team_name, {}).get(source_name, source_name)


def localize_player_position(team_name, source_name, source_position):
    source_name = (source_name or "").strip()
    source_position = (source_position or "").strip()

    manual = PLAYER_POSITION_OVERRIDES.get(team_name, {}).get(source_name)
    if manual:
        return manual

    normalized = source_position.casefold()
    for english, russian in POSITION_TRANSLATIONS.items():
        if english in normalized:
            return russian
    return source_position


def parse_transfermarkt_players(html, page_url):
    players = []
    seen = set()
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.IGNORECASE | re.DOTALL)

    for row in rows:
        if "spieler" not in row and "profil/spieler" not in row:
            continue

        link_match = re.search(
            r'href="(?P<href>/[^"]+/(?:profil/spieler|spieler)/\d+[^"]*)"'
            r'(?:[^>]*title="(?P<title>[^"]+)")?[^>]*>(?P<label>.*?)</a>',
            row,
            re.IGNORECASE | re.DOTALL,
        )
        if not link_match:
            continue

        name = clean_text(link_match.group("title") or link_match.group("label"))
        if not name:
            continue

        normalized_name = name.casefold()
        if normalized_name in seen:
            continue
        seen.add(normalized_name)

        row_text = clean_text(row)
        position = parse_position_from_text(row_text)
        players.append(
            {
                "name": name,
                "position": position,
                "source_url": urljoin(page_url, link_match.group("href").split("?")[0]),
            }
        )

    return players


def parse_astana_players_official(html, page_url):
    players = []
    seen = set()
    cards = re.findall(
        r'<a[^>]+href="(?P<href>/en/players/view/\d+[^"]*)"[^>]*>(?P<body>.*?)</a>',
        html,
        re.IGNORECASE | re.DOTALL,
    )

    for href, body in cards:
        name_match = re.search(
            r'players-item__(?:title|name)[^>]*>(?P<name>.*?)</',
            body,
            re.IGNORECASE | re.DOTALL,
        )
        if not name_match:
            name_match = re.search(r'alt="(?P<name>[^"]+)"', body, re.IGNORECASE)
        if not name_match:
            continue

        name = clean_text(name_match.group("name"))
        if not name:
            continue

        normalized_name = name.casefold()
        if normalized_name in seen:
            continue
        seen.add(normalized_name)

        body_text = clean_text(body)
        players.append(
            {
                "name": name,
                "position": parse_position_from_text(body_text),
                "source_url": urljoin(page_url, href.split("?")[0]),
            }
        )

    return players


def parse_transfermarkt_coach(html, page_url):
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.IGNORECASE | re.DOTALL)
    for row in rows:
        row_text = clean_text(row)
        lowered = row_text.lower()
        if not any(keyword in lowered for keyword in COACH_ROLE_KEYWORDS):
            continue

        link_match = re.search(
            r'href="(?P<href>/[^"]+/(?:trainer|profil)/[^"]+)"'
            r'(?:[^>]*title="(?P<title>[^"]+)")?[^>]*>(?P<label>.*?)</a>',
            row,
            re.IGNORECASE | re.DOTALL,
        )
        if not link_match:
            link_match = re.search(
                r'href="(?P<href>/[^"]+)"(?:[^>]*title="(?P<title>[^"]+)")?[^>]*>(?P<label>.*?)</a>',
                row,
                re.IGNORECASE | re.DOTALL,
            )
        if not link_match:
            continue

        name = clean_text(link_match.group("title") or link_match.group("label"))
        if not name:
            continue

        return {
            "name": name,
            "position": "Head coach",
            "source_url": urljoin(page_url, link_match.group("href").split("?")[0]),
        }
    return None


def parse_astana_coach_from_article(html, page_url):
    headline_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    headline = clean_text(headline_match.group(1)) if headline_match else extract_title(html)
    if not headline:
        return None

    primary_part = re.split(r"[|:—-]", headline, maxsplit=1)[0].strip()
    name_match = re.match(r"([A-Z][A-Za-z'.-]+(?:\s+[A-Z][A-Za-z'.-]+)+)", primary_part)
    if not name_match:
        return None

    return {
        "name": name_match.group(1).strip(),
        "position": "Head coach",
        "source_url": page_url,
    }


class Command(BaseCommand):
    help = "Disabled: teams are managed only through the database and Dashboard."

    def handle(self, *args, **options):
        raise CommandError(
            "Команда отключена. Раздел Teams больше не обновляется из внешних источников; "
            "используйте Dashboard для ручного управления командами и игроками."
        )

        astana_coach = None
        try:
            astana_coach_html = fetch_html(ASTANA_COACH_ARTICLE_URL)
            astana_coach = parse_astana_coach_from_article(astana_coach_html, ASTANA_COACH_ARTICLE_URL)
        except Exception:
            astana_coach = None

        if not astana_coach:
            try:
                astana_staff_html = fetch_html(ASTANA_TRANSFERMARKT_STAFF_URL)
                astana_coach = parse_transfermarkt_coach(
                    astana_staff_html,
                    ASTANA_TRANSFERMARKT_STAFF_URL,
                )
            except Exception:
                astana_coach = None

        if not astana_coach:
            astana_coach = {
                "name": ASTANA_COACH_FALLBACK_NAME,
                "position": "Head coach",
                "source_url": ASTANA_TRANSFERMARKT_STAFF_URL,
            }

        kairat_coach = parse_transfermarkt_coach(kairat_staff_html, KAIRAT_TRANSFERMARKT_STAFF_URL)
        if not kairat_coach:
            kairat_coach = {
                "name": KAIRAT_COACH_FALLBACK_NAME,
                "position": "Head coach",
                "source_url": KAIRAT_TRANSFERMARKT_STAFF_URL,
            }

        if len(astana_players) < 11:
            raise CommandError(
                f"Не удалось собрать минимальный состав Astana: найдено только {len(astana_players)} игроков."
            )
        if len(kairat_players) < 11:
            raise CommandError(
                f"Не удалось собрать минимальный состав Kairat: найдено только {len(kairat_players)} игроков."
            )
        if not astana_coach:
            raise CommandError("Не удалось определить главного тренера Astana.")
        verified_at = timezone.now()
        stats = {
            "teams_created": 0,
            "teams_updated": 0,
            "players_created": 0,
            "players_updated": 0,
        }

        with transaction.atomic():
            kairat_team = self._upsert_team(
                name="Кайрат",
                city="Алматы",
                description="Футбольный клуб из Алматы, Казахстан.",
                source_url=KAIRAT_TRANSFERMARKT_SQUAD_URL,
                verified_at=verified_at,
                stats=stats,
            )
            astana_team = self._upsert_team(
                name="Астана",
                city="Астана",
                description="Футбольный клуб из Астаны, Казахстан.",
                source_url=ASTANA_OFFICIAL_PLAYERS_URL,
                verified_at=verified_at,
                stats=stats,
            )

            self._remove_demo_placeholders(kairat_team)
            self._remove_demo_placeholders(astana_team)
            kairat_payload = kairat_players + [kairat_coach]
            astana_payload = astana_players + [astana_coach]

            self._prune_imported_players(kairat_team, kairat_payload)
            self._prune_imported_players(astana_team, astana_payload)

            self._upsert_players(kairat_team, kairat_payload, verified_at, stats)
            self._upsert_players(astana_team, astana_payload, verified_at, stats)

        self.stdout.write(self.style.SUCCESS("Импорт футбольных команд завершен успешно."))
        self.stdout.write(
            "Команд создано: {teams_created}, обновлено: {teams_updated}. "
            "Игроков/тренеров создано: {players_created}, обновлено: {players_updated}.".format(**stats)
        )

    def _merge_players(self, primary_players, fallback_players):
        merged = []
        seen = set()
        for item in list(primary_players) + list(fallback_players):
            name = (item.get("name") or "").strip()
            if not name:
                continue
            key = name.casefold()
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)
        return merged

    def _upsert_team(self, name, city, description, source_url, verified_at, stats):
        team, created = Team.objects.update_or_create(
            name=name,
            defaults={
                "kind": Team.KIND_SPORT,
                "discipline": Team.DISCIPLINE_FOOTBALL,
                "city": city,
                "country": "Kazakhstan",
                "description": description,
                "source_url": source_url,
                "source_updated_at": verified_at,
                "is_manual": True,
                "is_active": True,
            },
        )
        stats["teams_created" if created else "teams_updated"] += 1
        return team

    def _remove_demo_placeholders(self, team):
        team.players.filter(name__in=PLACEHOLDER_NAMES).delete()

    def _prune_imported_players(self, team, players):
        imported_names = {
            localize_player_name(team.name, (item.get("name") or "").strip())
            for item in players
            if item.get("name")
        }
        if not imported_names:
            return

        team.players.exclude(name__in=imported_names).filter(
            Q(source_url__gt="") | Q(last_verified_at__isnull=False)
        ).delete()

    def _upsert_players(self, team, players, verified_at, stats):
        for item in players:
            source_name = (item.get("name") or "").strip()
            if not source_name:
                continue
            name = localize_player_name(team.name, source_name)

            defaults = {
                "position": localize_player_position(
                    team.name,
                    source_name,
                    (item.get("position") or "").strip(),
                ),
                "bio": "",
                "source_url": (item.get("source_url") or "").strip(),
                "last_verified_at": verified_at,
            }
            player, created = Player.objects.update_or_create(
                team=team,
                name=name,
                defaults=defaults,
            )
            stats["players_created" if created else "players_updated"] += 1
            self.stdout.write(
                f"[{team.name}] {'created' if created else 'updated'}: {player.name}"
            )
