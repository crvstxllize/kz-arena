from django.contrib.auth.models import Group

EDITORS_GROUP_NAME = "Editors"


def is_admin(user):
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.is_staff


def is_editor(user):
    if not user or not user.is_authenticated:
        return False
    return (not is_admin(user)) and user.groups.filter(name=EDITORS_GROUP_NAME).exists()


def can_manage_users(user):
    return is_admin(user)


def can_edit_articles(user):
    return is_admin(user) or is_editor(user)


def get_role_key(user):
    if is_admin(user):
        return "admin"
    if is_editor(user):
        return "editor"
    return "user"


def get_role_label(user):
    role = get_role_key(user)
    if role == "admin":
        return "Администратор"
    if role == "editor":
        return "Редактор"
    return "Пользователь"


def set_user_role(user, role):
    editors_group, _ = Group.objects.get_or_create(name=EDITORS_GROUP_NAME)

    if role == "admin":
        user.is_staff = True
        user.is_superuser = False
        user.groups.remove(editors_group)
        user.save(update_fields=["is_staff", "is_superuser"])
        return

    if role == "editor":
        user.is_staff = False
        user.is_superuser = False
        user.save(update_fields=["is_staff", "is_superuser"])
        user.groups.add(editors_group)
        return

    if role == "user":
        user.is_staff = False
        user.is_superuser = False
        user.groups.remove(editors_group)
        user.save(update_fields=["is_staff", "is_superuser"])
        return

    raise ValueError("Unknown role.")
