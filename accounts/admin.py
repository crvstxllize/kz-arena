from django import forms
from django.contrib import admin, messages
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group, User
from django.db.models import Q

from .models import Profile
from .roles import (
    EDITORS_GROUP_NAME,
    can_manage_users,
    get_role_key,
    get_role_label,
    set_user_role,
)

ROLE_CHOICES = (
    ("admin", "Администратор"),
    ("editor", "Редактор"),
    ("user", "Пользователь"),
)


class UserRoleChangeForm(UserChangeForm):
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label="Роль",
        help_text="Выберите одну из ролей: Администратор / Редактор / Пользователь.",
    )

    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["role"].initial = get_role_key(self.instance)


class UserRoleCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        initial="user",
        label="Роль",
        help_text="Выберите одну из ролей: Администратор / Редактор / Пользователь.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")


class ProfileModerationForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label="Роль",
        help_text="Выберите одну из ролей: Администратор / Редактор / Пользователь.",
    )
    is_active = forms.BooleanField(
        required=False,
        label="Активен",
        help_text="Снимите галочку, чтобы забанить пользователя.",
    )

    class Meta:
        model = Profile
        fields = ("user", "display_name", "avatar", "role", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.instance.user if self.instance and self.instance.pk else None
        if user:
            self.fields["role"].initial = get_role_key(user)
            self.fields["is_active"].initial = user.is_active

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
                groups__name=EDITORS_GROUP_NAME,
            ).distinct()
        if value == "user":
            return queryset.exclude(
                Q(is_superuser=True) | Q(is_staff=True) | Q(groups__name=EDITORS_GROUP_NAME)
            ).distinct()
        return queryset


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileModerationForm
    list_display = ("user", "role_display", "is_active_display", "display_name", "created_at")
    search_fields = ("user__username", "user__email", "display_name")
    list_select_related = ("user",)
    list_filter = (UserRoleListFilter, "user__is_active")
    fields = ("user", "display_name", "avatar", "role", "is_active")
    actions = (
        "set_role_admin",
        "set_role_editor",
        "set_role_user",
        "ban_profiles",
        "unban_profiles",
    )

    @admin.display(description="Роль")
    def role_display(self, obj):
        return get_role_label(obj.user)

    @admin.display(description="Активен", boolean=True)
    def is_active_display(self, obj):
        return obj.user.is_active

    @admin.action(description='Назначить роль "Администратор"')
    def set_role_admin(self, request, queryset):
        updated = 0
        for profile in queryset.select_related("user"):
            set_user_role(profile.user, "admin")
            updated += 1
        self.message_user(request, f"Роль администратора назначена: {updated}.")

    @admin.action(description='Назначить роль "Редактор"')
    def set_role_editor(self, request, queryset):
        updated = 0
        for profile in queryset.select_related("user"):
            set_user_role(profile.user, "editor")
            updated += 1
        self.message_user(request, f"Роль редактора назначена: {updated}.")

    @admin.action(description='Назначить роль "Пользователь"')
    def set_role_user(self, request, queryset):
        updated = 0
        for profile in queryset.select_related("user"):
            set_user_role(profile.user, "user")
            updated += 1
        self.message_user(request, f'Роль "Пользователь" назначена: {updated}.')

    @admin.action(description="Забанить выбранные профили (is_active=False)")
    def ban_profiles(self, request, queryset):
        updated = 0
        skipped_self = 0
        for profile in queryset.select_related("user"):
            if profile.user_id == request.user.id:
                skipped_self += 1
                continue
            if profile.user.is_active:
                profile.user.is_active = False
                profile.user.save(update_fields=["is_active"])
                updated += 1
        if skipped_self:
            self.message_user(
                request,
                "Текущий пользователь пропущен (нельзя забанить самого себя).",
                level=messages.WARNING,
            )
        self.message_user(request, f"Забанено пользователей: {updated}.")

    @admin.action(description="Разбанить выбранные профили (is_active=True)")
    def unban_profiles(self, request, queryset):
        updated = 0
        for profile in queryset.select_related("user"):
            if not profile.user.is_active:
                profile.user.is_active = True
                profile.user.save(update_fields=["is_active"])
                updated += 1
        self.message_user(request, f"Разбанено пользователей: {updated}.")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        role = form.cleaned_data.get("role")
        is_active = form.cleaned_data.get("is_active", True)

        if obj.user_id == request.user.id and not is_active:
            self.message_user(
                request,
                "Нельзя забанить самого себя через админку.",
                level=messages.WARNING,
            )
            is_active = True

        if role:
            set_user_role(obj.user, role)

        if obj.user.is_active != is_active:
            obj.user.is_active = is_active
            obj.user.save(update_fields=["is_active"])

    def has_module_permission(self, request):
        return can_manage_users(request.user)

    def has_view_permission(self, request, obj=None):
        return can_manage_users(request.user)

    def has_add_permission(self, request):
        return can_manage_users(request.user)

    def has_change_permission(self, request, obj=None):
        return can_manage_users(request.user)

    def has_delete_permission(self, request, obj=None):
        return can_manage_users(request.user)


try:
    admin.site.unregister(User)
except NotRegistered:
    pass


try:
    admin.site.unregister(Group)
except NotRegistered:
    pass


@admin.register(Group)
class GroupAdmin(DjangoGroupAdmin):
    def has_module_permission(self, request):
        return can_manage_users(request.user)

    def has_view_permission(self, request, obj=None):
        return can_manage_users(request.user)

    def has_add_permission(self, request):
        return can_manage_users(request.user)

    def has_change_permission(self, request, obj=None):
        return can_manage_users(request.user)

    def has_delete_permission(self, request, obj=None):
        return can_manage_users(request.user)


@admin.register(User)
class UserModerationAdmin(DjangoUserAdmin):
    form = UserRoleChangeForm
    add_form = UserRoleCreationForm
    inlines = (ProfileInline,)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Роль и доступ",
            {
                "fields": (
                    "role",
                    "is_active",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "role",
                ),
            },
        ),
    )
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
    search_fields = ("username", "email", "first_name", "last_name", "profile__display_name")
    list_filter = (UserRoleListFilter, "is_active", "is_staff", "is_superuser", "groups")
    actions = (
        "set_role_admin",
        "set_role_editor",
        "set_role_user",
        "ban_users",
        "unban_users",
    )

    @admin.display(description="Роль")
    def role_display(self, obj):
        return get_role_label(obj)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        role = form.cleaned_data.get("role")
        if form.instance.pk == request.user.pk and role != "admin":
            self.message_user(
                request,
                "Нельзя снять у самого себя роль администратора через админку.",
                level=messages.WARNING,
            )
            role = "admin"
        if role:
            set_user_role(form.instance, role)

    def save_model(self, request, obj, form, change):
        if obj.pk == request.user.pk and not form.cleaned_data.get("is_active", True):
            self.message_user(
                request,
                "Нельзя забанить самого себя через админку.",
                level=messages.WARNING,
            )
            obj.is_active = True
        super().save_model(request, obj, form, change)

    @admin.action(description='Назначить роль "Администратор"')
    def set_role_admin(self, request, queryset):
        updated = 0
        for user in queryset:
            set_user_role(user, "admin")
            updated += 1
        self.message_user(request, f"Роль администратора назначена: {updated}.")

    @admin.action(description='Назначить роль "Редактор"')
    def set_role_editor(self, request, queryset):
        updated = 0
        for user in queryset:
            set_user_role(user, "editor")
            updated += 1
        self.message_user(request, f"Роль редактора назначена: {updated}.")

    @admin.action(description='Назначить роль "Пользователь"')
    def set_role_user(self, request, queryset):
        updated = 0
        for user in queryset:
            set_user_role(user, "user")
            updated += 1
        self.message_user(request, f'Роль "Пользователь" назначена: {updated}.')

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
        updated = 0
        for user in queryset:
            if not user.is_active:
                user.is_active = True
                user.save(update_fields=["is_active"])
                updated += 1
        self.message_user(request, f"Разбанено пользователей: {updated}.")

    def has_module_permission(self, request):
        return can_manage_users(request.user)

    def has_view_permission(self, request, obj=None):
        return can_manage_users(request.user)

    def has_add_permission(self, request):
        return can_manage_users(request.user)

    def has_change_permission(self, request, obj=None):
        return can_manage_users(request.user)

    def has_delete_permission(self, request, obj=None):
        return can_manage_users(request.user)
