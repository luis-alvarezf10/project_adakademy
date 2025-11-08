from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('classroom/', views.classroom, name='classroom'),
    path('manage-evaluations/', views.manage_evaluations, name='manage_evaluations'),
    path('create-evaluation/', views.create_evaluation, name='create_evaluation'),
    path('grade-evaluation/<int:eval_id>/', views.grade_evaluation, name='grade_evaluation'),
    path('delete-evaluation/<int:eval_id>/', views.delete_evaluation, name='delete_evaluation'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('my-subjects/', views.my_subjects, name='my_subjects'),
    path('subject/<str:subject_name>/', views.subject_detail, name='subject_detail'),
    path('teacher-subjects/', views.teacher_subjects, name='teacher_subjects'),
    path('student-reports/', views.student_reports, name='student_reports'),
    path('student-report/<str:student_ci>/', views.generate_student_report, name='generate_student_report'),
    path('update-evaluations/', views.update_evaluations, name='update_evaluations'),
    path('logout/', views.logout_view, name='logout'),
]