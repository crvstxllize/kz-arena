from django.shortcuts import render


def news_list(request):
    featured_news = {
        "title": "Сборная Казахстана по CS2 вышла в финал регионального чемпионата",
        "excerpt": "Решающая серия завершилась со счетом 2:1. Команда сыграет за титул уже в эту субботу.",
        "published_at": "12 февраля 2026",
        "image_url": "https://picsum.photos/seed/kz-featured-news/1000/560",
        "kind": "esport",
        "discipline": "CS2",
        "category": "Киберспорт",
        "url": "#",
        "urgent": True,
    }

    top_day = [
        {"title": "Клуб из Алматы подписал нового разыгрывающего", "published_at": "12 февраля", "discipline": "Баскетбол", "kind": "sport", "url": "#"},
        {"title": "Dota 2: определены участники закрытых отборов", "published_at": "12 февраля", "discipline": "Dota 2", "kind": "esport", "url": "#"},
        {"title": "Футбольная Премьер-лига опубликовала календарь тура", "published_at": "11 февраля", "discipline": "Футбол", "kind": "sport", "url": "#"},
        {"title": "PUBG-команда из Астаны вышла на LAN-финал", "published_at": "11 февраля", "discipline": "PUBG", "kind": "esport", "url": "#"},
    ]

    all_news = [
        {"title": "Футбол: молодежная сборная выиграла товарищеский матч", "excerpt": "Тренерский штаб протестировал новую схему с высоким прессингом.", "published_at": "12 февраля 2026", "image_url": "https://picsum.photos/seed/kz-news-1/640/360", "kind": "sport", "discipline": "Футбол", "category": "Спорт", "url": "#", "urgent": False},
        {"title": "Баскетбол: астанинский клуб начал серию домашних игр", "excerpt": "Первый матч недели завершился с разницей в девять очков.", "published_at": "12 февраля 2026", "image_url": None, "kind": "sport", "discipline": "Баскетбол", "category": "Спорт", "url": "#", "urgent": False},
        {"title": "CS2: казахстанский состав сохранил место в рейтинге топ-20", "excerpt": "Команда успешно прошла групповую стадию после двух напряженных карт.", "published_at": "11 февраля 2026", "image_url": "https://picsum.photos/seed/kz-news-3/640/360", "kind": "esport", "discipline": "CS2", "category": "Киберспорт", "url": "#", "urgent": False},
        {"title": "Dota 2: объявлен состав участников весеннего кубка", "excerpt": "В сетке восемь команд, первые матчи стартуют в следующую пятницу.", "published_at": "11 февраля 2026", "image_url": None, "kind": "esport", "discipline": "Dota 2", "category": "Киберспорт", "url": "#", "urgent": False},
        {"title": "PUBG: лига Central Asia Masters расширила призовой фонд", "excerpt": "Призовой пул увеличен на 20%, финал пройдет в Алматы.", "published_at": "10 февраля 2026", "image_url": "https://picsum.photos/seed/kz-news-5/640/360", "kind": "esport", "discipline": "PUBG", "category": "Киберспорт", "url": "#", "urgent": False},
        {"title": "Футбол: клубы согласовали новые стандарты медиа-дня", "excerpt": "Матчи будут сопровождаться расширенной предматчевой аналитикой.", "published_at": "10 февраля 2026", "image_url": None, "kind": "sport", "discipline": "Футбол", "category": "Спорт", "url": "#", "urgent": False},
    ]

    return render(
        request,
        "articles/news_list.html",
        {
            "page_title": "Новости",
            "page_description": "Главные новости спорта и киберспорта Казахстана.",
            "featured_news": featured_news,
            "top_day": top_day,
            "all_news": all_news,
            "breadcrumbs": [
                {"label": "Главная", "url": "core:home"},
                {"label": "Новости", "url": None},
            ],
        },
    )
