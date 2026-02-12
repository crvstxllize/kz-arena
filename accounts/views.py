from django.shortcuts import render


def account_home(request):
    return render(
        request,
        "core/page.html",
        {
            "page_title": "Accounts",
            "page_description": "Authentication and user profile module placeholder.",
            "breadcrumbs": [
                {"label": "Home", "url": "core:home"},
                {"label": "Accounts", "url": None},
            ],
        },
    )
