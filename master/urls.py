from django.urls import path
from . import views

app_name = 'master'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    # Member
    path('member/create/', views.MemberCreateView.as_view(), name='member_create'),
    path('member/<int:pk>/edit/', views.MemberUpdateView.as_view(), name='member_edit'),
    path('member/<int:pk>/delete/', views.MemberDeleteView.as_view(), name='member_delete'),
    # Project
    path('project/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('project/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_edit'),
    path('project/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    # Task
    path('task/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('task/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_edit'),
    path('task/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
]
