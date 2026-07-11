from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('create/', views.ScheduleCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.ScheduleUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ScheduleDeleteView.as_view(), name='delete'),
    path('<int:pk>/hours/', views.HoursUpdateView.as_view(), name='hours_update'),
    path('<int:pk>/resize/', views.ScheduleResizeView.as_view(), name='resize'),
    path('<int:pk>/move/', views.ScheduleMoveView.as_view(), name='move'),
    path('quick-create/', views.ScheduleQuickCreateView.as_view(), name='quick_create'),
]
