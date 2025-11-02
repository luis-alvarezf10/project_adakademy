from django.db import models

#### Tabla de Profesores

class Teacher(models.Model):
    username = models.CharField(max_length=50, unique=True)
    name =  models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    ci = models.CharField(primary_key=True, max_length=20, unique=True)
    email = models.EmailField(unique=True, max_length=80)
    password = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"

    def __str__(self):
        return self.name + " " + self.last_name

#### Tabla de Estudiantes

class Student(models.Model):
    username = models.CharField(max_length=50, unique=True)
    name =  models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    ci = models.CharField(primary_key=True, max_length=20, unique=True)
    password = models.CharField(max_length=20)
    email = models.EmailField(unique=True, max_length=80)
    grade = models.IntegerField(default=1)
    
    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return self.name + " " + self.last_name

#### Tabla de Materia

class Course(models.Model):
    name_course = models.CharField(max_length=20)
    teacher = models.ForeignKey(Teacher, verbose_name='assigned teacher', on_delete=models.SET_NULL, null=True, blank=True)
    grade = models.IntegerField(default=1)


    def __str__(self):
        return self.name_course


#### Tabla de Evaluacion

class Evaluation(models.Model):
    date = models.DateTimeField()
    subject = models. CharField(max_length=40)
    type = models.CharField(max_length=20)

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.subject

#### Tabla de Puntuacion

class Punctuation(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    
#### Tabla de Administradores

class Admin(models.Model):
    username = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    position = models.CharField(max_length=50)
    ci = models.CharField(primary_key=True, max_length=20, unique=True)
    email = models.EmailField(unique=True, max_length=80)
    password = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Admin"
        verbose_name_plural = "Admins"

    def __str__(self):
        return self.name_admin



