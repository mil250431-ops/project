from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('analyze/', views.analyze, name='analyze'),
    path('result/<int:analysis_id>/', views.result, name='result'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('delete/<int:analysis_id>/', views.delete_analysis, name='delete_analysis'),
    path('api/synonyms/', views.get_synonyms, name='get_synonyms'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]