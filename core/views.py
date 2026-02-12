from django.shortcuts import render


def home(request):
    latest_news = [
        {
            "title": "Сборная Казахстана U-21 вышла в финальную часть молодежного турнира",
            "excerpt": "Команда оформила уверенную победу в решающем матче квалификации.",
            "published_at": "12 февраля 2026",
            "image_url": "https://picsum.photos/seed/kz-home-1/640/360",
            "kind": "sport",
            "discipline": "Футбол",
            "category": "Футбол",
            "url": "#",
            "urgent": True,
        },
        {
            "title": "Алматинский клуб по баскетболу усилил состав перед плей-офф",
            "excerpt": "В заявку добавлены два опытных игрока на позиции защитника.",
            "published_at": "12 февраля 2026",
            "image_url": None,
            "kind": "sport",
            "discipline": "Баскетбол",
            "category": "Баскетбол",
            "url": "#",
            "urgent": False,
        },
        {
            "title": "Казахстанская пятерка по CS2 прошла в закрытую квалификацию",
            "excerpt": "Команда выиграла три матча подряд и закрепилась в верхней сетке.",
            "published_at": "11 февраля 2026",
            "image_url": "https://picsum.photos/seed/kz-home-3/640/360",
            "kind": "esport",
            "discipline": "CS2",
            "category": "CS2",
            "url": "#",
            "urgent": False,
        },
        {
            "title": "Dota 2: столичный состав объявил нового капитана",
            "excerpt": "Изменения в роли драфтера должны усилить раннюю стадию игры.",
            "published_at": "11 февраля 2026",
            "image_url": None,
            "kind": "esport",
            "discipline": "Dota 2",
            "category": "Dota 2",
            "url": "#",
            "urgent": False,
        },
        {
            "title": "PUBG-лига Центральной Азии стартует в конце месяца",
            "excerpt": "Организаторы представили формат группового этапа и расписание трансляций.",
            "published_at": "10 февраля 2026",
            "image_url": "https://picsum.photos/seed/kz-home-5/640/360",
            "kind": "esport",
            "discipline": "PUBG",
            "category": "PUBG",
            "url": "#",
            "urgent": False,
        },
        {
            "title": "Федерация футбола представила календарь весеннего тура",
            "excerpt": "Ключевые встречи тура запланированы на вечерние слоты выходных.",
            "published_at": "10 февраля 2026",
            "image_url": None,
            "kind": "sport",
            "discipline": "Футбол",
            "category": "Футбол",
            "url": "#",
            "urgent": False,
        },
    ]

    return render(
        request,
        "core/home.html",
        {
            "latest_news": latest_news,
            "page_title": "Главная",
            "page_description": "KZ Arena: новости спорта и киберспорта Казахстана.",
            "breadcrumbs": [],
        },
    )


def about(request):
    return render(
        request,
        "core/about.html",
        {
            "page_title": "О проекте",
            "page_description": "Что такое KZ Arena и для кого мы его создаем.",
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "О проекте", "url": None},
            ],
        },
    )


def custom_404(request, exception):
    return render(request, "core/404.html", status=404)


def custom_500(request):
    return render(request, "core/500.html", status=500)
