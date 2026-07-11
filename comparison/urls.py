from django.urls import path
from . import views

app_name = 'comparison'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
]
