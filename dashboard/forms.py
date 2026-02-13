from django import forms
from django.forms import CheckboxSelectMultiple

from articles.models import Article, MediaAsset


class DashboardArticleForm(forms.ModelForm):
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
        }


class MediaAssetForm(forms.ModelForm):
    class Meta:
        model = MediaAsset
        fields = ["file", "caption"]
