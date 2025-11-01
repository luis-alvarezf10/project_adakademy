from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('evaluations/', views.manage_evaluations, name='manage_evaluations'),
    path('create-evaluation/', views.create_evaluation, name='create_evaluation'),
    path('edit-evaluation/<int:eval_id>/', views.edit_evaluation, name='edit_evaluation'),
    path('update-evaluation/<int:eval_id>/', views.update_evaluation, name='update_evaluation'),
    path('delete-evaluation/<int:eval_id>/', views.delete_evaluation, name='delete_evaluation'),
    path('logout/', views.logout_view, name='logout'),
]