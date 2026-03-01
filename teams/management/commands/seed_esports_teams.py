from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from teams.models import Player, Team


NOVAQ_TEAM = {
    "name": "NOVAQ",
    "kind": Team.KIND_ESPORT,
    "discipline": Team.DISCIPLINE_CS2,
    "country": "Kazakhstan",
    "city": "",
    "description": (
        "Казахстанская команда по Counter-Strike 2. "
        "Текущий основной состав подтвержден по Liquipedia и HLTV."
    ),
    "source_url": "https://liquipedia.net/counterstrike/NOVAQ",
    "players": [
        {
            "name": "neaLaN",
            "position": "In-game leader / Support",
            "bio": (
                "Санжар Исхаков — профессиональный игрок из Казахстана. "
                "По данным Liquipedia выступает за NOVAQ и совмещает роли "
                "in-game leader и support."
            ),
            "source_url": "https://liquipedia.net/counterstrike/NeaLaN",
        },
        {
            "name": "ICY",
            "position": "AWPer",
            "bio": (
                "Кайсар Файзнуров — профессиональный игрок из Казахстана. "
                "По данным Liquipedia играет за NOVAQ на правах аренды и "
                "исполняет роль AWPer."
            ),
            "source_url": "https://liquipedia.net/counterstrike/ICY",
        },
        {
            "name": "def1zer",
            "position": "In-game leader / Rifler",
            "bio": (
                "Санжар Талгат — профессиональный игрок из Казахстана. "
                "По данным Liquipedia в составе NOVAQ выполняет роли "
                "in-game leader и rifler."
            ),
            "source_url": "https://liquipedia.net/counterstrike/Def1zer",
        },
        {
            "name": "Pump",
            "position": "",
            "bio": (
                "Данияр Булдыбаев — профессиональный игрок из Казахстана. "
                "По данным Liquipedia входит в основной состав NOVAQ."
            ),
            "source_url": "https://liquipedia.net/counterstrike/Pump",
        },
        {
            "name": "tasman",
            "position": "Rifler",
            "bio": (
                "Алишер Марат — профессиональный игрок из Казахстана. "
                "По данным Liquipedia выступает за NOVAQ в роли rifler."
            ),
            "source_url": "https://liquipedia.net/counterstrike/Tasman",
        },
    ],
}


GOLDEN_BARYS_TEAM = {
    "name": "Golden Barys",
    "kind": Team.KIND_ESPORT,
    "discipline": Team.DISCIPLINE_DOTA2,
    "country": "Russian Federation",
    "city": "",
    "description": (
        "Команда по Dota 2, подтвержденная по страницам квалификации Liquipedia "
        "и составу Escorenews."
    ),
    "source_url": "https://escorenews.com/en/dota-2/team/golden-barys",
    "players": [
        {
            "name": "Gazyava",
            "position": "Carry",
            "bio": (
                "Nurislam Mukhametyarov — игрок из России. "
                "По данным Escorenews выступает на позиции carry."
            ),
            "source_url": "https://escorenews.com/en/dota-2/player/gazyava",
        },
        {
            "name": "Volshebnik",
            "position": "Mid",
            "bio": (
                "Andrei Pekur — игрок из Украины. "
                "По данным Escorenews выступает на позиции mid."
            ),
            "source_url": "https://escorenews.com/en/dota-2/player/volshebnik",
        },
        {
            "name": "Modeto",
            "position": "Offlane",
            "bio": (
                "Shakhmardan Turginbek — игрок из Казахстана. "
                "По данным Escorenews выступает на позиции offlane."
            ),
            "source_url": "https://escorenews.com/en/dota-2/player/modeto",
        },
        {
            "name": "ArrOw",
            "position": "Support",
            "bio": (
                "Islambek Saudabaev — игрок из Казахстана. "
                "По данным Escorenews выступает на позиции support."
            ),
            "source_url": "https://escorenews.com/en/dota-2/player/arrow",
        },
        {
            "name": "Macao",
            "position": "Support",
            "bio": (
                "Полное имя на Escorenews не указано. "
                "Источник подтверждает никнейм Macao, страну Россия и роль support."
            ),
            "source_url": "https://escorenews.com/en/dota-2/player/macao",
        },
    ],
}


class Command(BaseCommand):
    help = "Disabled: teams are managed only through the database and Dashboard."

    def handle(self, *args, **options):
        raise CommandError(
            "Команда отключена. Раздел Teams больше не обновляется из внешних источников; "
            "используйте Dashboard для ручного управления командами и игроками."
        )

    def _upsert_team_with_players(self, payload, verified_at, stats):
        team, created = Team.objects.update_or_create(
            name=payload["name"],
            defaults={
                "kind": payload["kind"],
                "discipline": payload["discipline"],
                "country": payload["country"],
                "city": payload["city"],
                "description": payload["description"],
                "source_url": payload["source_url"],
                "source_updated_at": verified_at,
                "is_manual": True,
                "is_active": True,
            },
        )
        stats["teams_created" if created else "teams_updated"] += 1

        imported_names = {item["name"] for item in payload["players"]}
        team.players.exclude(name__in=imported_names).filter(source_url__gt="").delete()

        for item in payload["players"]:
            player, player_created = Player.objects.update_or_create(
                team=team,
                name=item["name"],
                defaults={
                    "position": item["position"],
                    "bio": item["bio"],
                    "source_url": item["source_url"],
                    "last_verified_at": verified_at,
                },
            )
            stats["players_created" if player_created else "players_updated"] += 1
            self.stdout.write(
                f"[{team.name}] {'created' if player_created else 'updated'}: {player.name}"
            )
