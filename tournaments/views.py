from django.shortcuts import render


def tournament_list(request):
    return render(
        request,
        "tournaments/tournament_list.html",
        {
            "page_title": "Турниры",
            "page_description": "Актуальные и предстоящие турниры по видам спорта и киберспорта.",
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Турниры", "url": None},
            ],
        },
    )


def match_list(request):
    return render(
        request,
        "tournaments/match_list.html",
        {
            "page_title": "Матчи",
            "page_description": "Расписание, результаты и статус текущих матчей.",
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Матчи", "url": None},
            ],
        },
    )
