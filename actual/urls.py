from django.urls import path
from . import views

app_name = 'actual'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('save/', views.ActualSaveView.as_view(), name='save'),
    path('<int:pk>/delete/', views.ActualDeleteView.as_view(), name='delete'),
]
