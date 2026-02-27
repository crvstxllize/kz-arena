from django.contrib import admin, messages
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import Q
from django.contrib.auth.models import User

from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0


class UserRoleListFilter(admin.SimpleListFilter):
    title = "роль"
    parameter_name = "role"

    def lookups(self, request, model_admin):
        return (
            ("admin", "Администратор"),
            ("editor", "Редактор"),
            ("user", "Пользователь"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "admin":
            return queryset.filter(Q(is_superuser=True) | Q(is_staff=True))
        if value == "editor":
            return queryset.filter(
                is_superuser=False,
                is_staff=False,
                groups__name="Editors",
            ).distinct()
        if value == "user":
            return queryset.exclude(
                Q(is_superuser=True) | Q(is_staff=True) | Q(groups__name="Editors")
            ).distinct()
        return queryset


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role_display", "display_name", "created_at")
    search_fields = ("user__username", "user__email", "display_name")
    list_select_related = ("user",)
    list_filter = (UserRoleListFilter,)

    @admin.display(description="Роль")
    def role_display(self, obj):
        user = obj.user
        if user.is_superuser or user.is_staff:
            return "Администратор"
        if user.groups.filter(name="Editors").exists():
            return "Редактор"
        return "Пользователь"


try:
    admin.site.unregister(User)
except NotRegistered:
    pass


@admin.register(User)
class UserModerationAdmin(DjangoUserAdmin):
    inlines = (ProfileInline,)
    list_display = (
        "username",
        "email",
        "role_display",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "last_login",
        "date_joined",
    )
    list_filter = (UserRoleListFilter, "is_active", "is_staff", "is_superuser", "groups")
    actions = ("ban_users", "unban_users")

    @admin.display(description="Роль")
    def role_display(self, obj):
        if obj.is_superuser or obj.is_staff:
            return "Администратор"
        if obj.groups.filter(name="Editors").exists():
            return "Редактор"
        return "Пользователь"

    @admin.action(description="Забанить выбранных пользователей (is_active=False)")
    def ban_users(self, request, queryset):
        target_qs = queryset.exclude(pk=request.user.pk)
        skipped_self = queryset.count() - target_qs.count()
        updated = target_qs.update(is_active=False)
        if skipped_self:
            self.message_user(
                request,
                "Текущий пользователь пропущен (нельзя забанить самого себя из админки).",
                level=messages.WARNING,
            )
        self.message_user(request, f"Забанено пользователей: {updated}.")

    @admin.action(description="Разбанить выбранных пользователей (is_active=True)")
    def unban_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Разбанено пользователей: {updated}.")
