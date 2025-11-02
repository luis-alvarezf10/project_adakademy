from django.contrib import admin
from .models import Student, Teacher, Course, Evaluation, Admin, Punctuation

class StudentAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'last_name', 'ci', 'email', 'grade')
    search_fields = ('username', 'name', 'last_name', 'email', 'ci')

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'last_name', 'ci', 'email')
    search_fields = ('username','name', 'last_name', 'email', 'ci')

class CourseAdmin(admin.ModelAdmin):
    list_display = ('name_course', 'teacher', 'grade')
    search_fields = ('name_course', 'teacher__name')

class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('date', 'subject', 'type', 'course')
    search_fields = ('subject', 'type', 'course__name_course')

class PunctuationAdmin(admin.ModelAdmin):
    list_display = ('evaluation', 'student', 'score')
    search_fields = ('evaluation__subject', 'student__name')

class AdminAdmin(admin.ModelAdmin):
    list_display = ('username','name', 'last_name', 'position', 'ci', 'email')
    search_fields = ('username', 'name', 'last_name', 'position', 'ci', 'email')

admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Evaluation, EvaluationAdmin)
admin.site.register(Admin, AdminAdmin)
admin.site.register(Punctuation, PunctuationAdmin)