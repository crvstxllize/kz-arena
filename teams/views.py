from django.shortcuts import render


def team_list(request):
    return render(
        request,
        "teams/team_list.html",
        {
            "page_title": "Команды",
            "page_description": "Составы команд и ключевые показатели по сезону.",
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Команды", "url": None},
            ],
        },
    )
