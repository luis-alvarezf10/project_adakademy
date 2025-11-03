from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('classroom/', views.classroom, name='classroom'),
    path('manage-evaluations/', views.manage_evaluations, name='manage_evaluations'),
    path('create-evaluation/', views.create_evaluation, name='create_evaluation'),
    path('delete-evaluation/<int:eval_id>/', views.delete_evaluation, name='delete_evaluation'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('my-subjects/', views.my_subjects, name='my_subjects'),
    path('subject/<str:subject_name>/', views.subject_detail, name='subject_detail'),
    path('update-evaluations/', views.update_evaluations, name='update_evaluations'),
    path('logout/', views.logout_view, name='logout'),
]