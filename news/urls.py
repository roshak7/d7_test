from django.urls import path
from .views import *

urlpatterns = [
    path('', NewsList.as_view()),
    path('<int:pk>', NewsDetail.as_view(), name='news_one'),
    path('search/', NewsSearch.as_view(), name='news_search'),
    path('add/', NewsAdd.as_view(), name='news_add'),
    path('edit/<int:pk>', NewsEdit.as_view(), name='news_update'),
    path('delete/<int:pk>', NewsDelete.as_view(), name='news_delete'),
    path('category/<int:category_id>', NewsOfCategory.as_view(), name='news_category'),
    path('category/<int:category_id>/subscribe', SubscribeView.as_view(), name='subscribe'),
    path('', IndexView.as_view()),
]
