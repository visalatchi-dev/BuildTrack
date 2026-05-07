from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('daily-log/', views.daily_log, name='daily_log'),
    path('issues/', views.issues, name='issues'),
    path('workers/', views.workers, name='workers'),
    path('workers/bulk-attendance/', views.bulk_attendance, name='bulk_attendance'),
    path('projects/add/', views.project_add, name='project_add'),
    path('projects/edit/<int:pk>/', views.project_edit, name='project_edit'),
    path('projects/delete/<int:pk>/', views.project_delete, name='project_delete'),
    path('workers/delete/<int:pk>/', views.worker_delete, name='worker_delete'),
    path('issues/delete/<int:pk>/', views.issue_delete, name='issue_delete'),
    path('users/', views.users_list, name='users_list'),
    path('users/add/', views.user_add, name='user_add'),
    path('users/promote/<int:pk>/', views.user_promote, name='user_promote'),
    path('users/delete/<int:pk>/', views.user_delete, name='user_delete'),
    path('users/edit/<int:pk>/', views.user_edit, name='user_edit'),
    path('daily-log/delete/<int:log_id>/', views.delete_log, name='delete_log'),
]