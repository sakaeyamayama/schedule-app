from django.urls import path
from . import views

app_name = 'importer'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('template/', views.download_template, name='template'),
]
