from django_filters import FilterSet, DateFilter
from django.forms import DateInput

from .models import Post


class PostFilter(FilterSet):
    date_less = DateFilter(field_name='creation_datetime',
                           lookup_expr='lt',
                           label='Less this date',
                           widget=DateInput(attrs={'type': 'date'}))

    date_after = DateFilter(field_name='creation_datetime',
                            lookup_expr='gt',
                            label='After this date',
                            widget=DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],
            'author': ['exact'],
        }
