from django import forms
from .models import Post


class NewsForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'category', 'type']
        widgets = {
            'title': forms.TextInput(attrs={"class": "form-control"}),
            'text': forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            'type': forms.Select(attrs={"class": "form-control"}),
            'category': forms.SelectMultiple(attrs={"class": "form-control"}),
        }
        labels = {
            'category': 'Категория'
        }
