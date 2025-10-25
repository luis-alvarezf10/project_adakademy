from django.db import models

# Create your models here.
#### Tabla de Profesores

class Teacher(models.Model):
    name_teacher =  models.CharField(max_length=50)
    ci = models.CharField(primary_key=True, max_length=20, unique=True)
    email = models.EmailField(unique=True, max_length=80)
    password = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Profesor"
        verbose_name_plural = "Profesores"

    def __str__(self):
        return self.name_teacher

#### Tabla de Estudiantes

class Student(models.Model):
    name_student =  models.CharField(max_length=50)
    ci = models.CharField(primary_key=True, max_length=20, unique=True)
    password = models.CharField(max_length=20)
    email = models.EmailField(unique=True, max_length=80)

    def __str__(self):
        return self.name_student

#### Tabla de Materia

class Course(models.Model):
    name_course = models.CharField(max_length=20)
    teacher = models.ForeignKey(Teacher, verbose_name='Profesor Asignado', on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return self.name_course


#### Tabla de Evaluacion

class Evaluation(models.Model):
    date = models.DateTimeField()
    subject = models. CharField(max_length=40)
    type = models.CharField(max_length=20)
    score = models.DecimalField(max_digits=5, decimal_places=2)

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)



