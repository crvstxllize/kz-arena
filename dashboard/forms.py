from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.forms import CheckboxSelectMultiple
from django.forms import inlineformset_factory

from articles.models import Article, MediaAsset
from teams.models import Player, Team

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024


def _validate_image_upload(upload, field_label):
    if not upload:
        return upload

    # Validate only new uploads from request.FILES.
    # Existing FieldFile values should pass through untouched.
    if not isinstance(upload, UploadedFile):
        return upload

    file_name = str(getattr(upload, "name", "") or "")
    lower_name = file_name.lower()
    if not any(lower_name.endswith(ext) for ext in ALLOWED_IMAGE_EXTENSIONS):
        allowed = ", ".join(sorted(ext.lstrip(".") for ext in ALLOWED_IMAGE_EXTENSIONS))
        raise forms.ValidationError(f"{field_label}: допустимы только файлы {allowed.upper()}.")

    file_size = getattr(upload, "size", 0) or 0
    if file_size > MAX_UPLOAD_SIZE_BYTES:
        max_mb = MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)
        raise forms.ValidationError(f"{field_label}: размер файла не должен превышать {max_mb} MB.")

    return upload


class DashboardArticleForm(forms.ModelForm):
    def clean_cover(self):
        return _validate_image_upload(self.cleaned_data.get("cover"), "Обложка")

    class Meta:
        model = Article
        fields = [
            "title",
            "excerpt",
            "content",
            "kind",
            "discipline",
            "categories",
            "tags",
            "cover",
            "is_featured",
        ]
        widgets = {
            "categories": CheckboxSelectMultiple(),
            "tags": CheckboxSelectMultiple(),
            "excerpt": forms.Textarea(attrs={"rows": 3}),
            "content": forms.Textarea(attrs={"rows": 10}),
            "cover": forms.ClearableFileInput(attrs={"accept": ".jpg,.jpeg,.png,.webp"}),
        }
        labels = {
            "title": "Заголовок",
            "excerpt": "Краткое описание",
            "content": "Текст статьи",
            "kind": "Тип",
            "discipline": "Дисциплина",
            "categories": "Категории",
            "tags": "Теги",
            "cover": "Обложка",
            "is_featured": "Показывать как главное",
        }
        help_texts = {
            "cover": "JPG, JPEG, PNG, WEBP. Максимальный размер 5 MB.",
            "categories": "Выберите одну или несколько категорий.",
            "tags": "Выберите подходящие теги для статьи.",
        }


class MediaAssetForm(forms.ModelForm):
    def clean_file(self):
        return _validate_image_upload(self.cleaned_data.get("file"), "Изображение")

    class Meta:
        model = MediaAsset
        fields = ["file", "caption"]
        widgets = {
            "file": forms.ClearableFileInput(attrs={"accept": ".jpg,.jpeg,.png,.webp"}),
            "caption": forms.TextInput(attrs={"placeholder": "Короткая подпись (необязательно)"}),
        }
        labels = {
            "file": "Файл изображения",
            "caption": "Подпись",
        }
        help_texts = {
            "file": "Можно добавлять свои изображения к статье (до 5 MB).",
        }


class TeamDashboardForm(forms.ModelForm):
    def clean_logo(self):
        return _validate_image_upload(self.cleaned_data.get("logo"), "Логотип")

    class Meta:
        model = Team
        fields = [
            "name",
            "slug",
            "kind",
            "discipline",
            "city",
            "country",
            "description",
            "logo",
            "source_url",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
        labels = {
            "name": "Название команды",
            "slug": "Slug",
            "kind": "Тип",
            "discipline": "Дисциплина",
            "city": "Город",
            "country": "Страна",
            "description": "Описание",
            "logo": "Логотип",
            "source_url": "Источник",
            "is_active": "Показывать на сайте",
        }
        help_texts = {
            "slug": "Оставьте пустым для авто-генерации.",
            "logo": "JPG, JPEG, PNG, WEBP. Максимальный размер 5 MB.",
            "source_url": "Ссылка на официальный или проверенный источник (опционально).",
        }


class TeamMemberForm(forms.ModelForm):
    def clean_photo(self):
        return _validate_image_upload(self.cleaned_data.get("photo"), "Фото игрока")

    class Meta:
        model = Player
        fields = ["name", "position", "bio", "photo"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 2}),
        }
        labels = {
            "name": "Игрок",
            "position": "Позиция/роль",
            "bio": "Описание",
            "photo": "Фото",
        }


TeamMemberFormSet = inlineformset_factory(
    Team,
    Player,
    form=TeamMemberForm,
    extra=3,
    can_delete=True,
    fields=["name", "position", "bio", "photo"],
)
