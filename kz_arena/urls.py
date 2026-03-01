from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path(
        "favicon.ico",
        RedirectView.as_view(url=f"{settings.STATIC_URL}img/kz-arena-favicon-32.png?v=2", permanent=False),
    ),
    path("admin/", admin.site.urls),
    path("", include(("core.urls", "core"), namespace="core")),
    path("news/", include(("articles.urls", "articles"), namespace="articles")),
    path("teams/", include(("teams.urls", "teams"), namespace="teams")),
    path(
        "tournaments/",
        include(("tournaments.urls", "tournaments"), namespace="tournaments"),
    ),
    path(
        "matches/",
        include(("tournaments.urls_matches", "matches"), namespace="matches"),
    ),
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("api/", include(("api.urls", "api"), namespace="api")),
    path("taxonomy/", include(("taxonomy.urls", "taxonomy"), namespace="taxonomy")),
    path("comments/", include(("comments.urls", "comments"), namespace="comments")),
    path(
        "interactions/",
        include(("interactions.urls", "interactions"), namespace="interactions"),
    ),
    path("dashboard/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "core.views.custom_404"
handler500 = "core.views.custom_500"
