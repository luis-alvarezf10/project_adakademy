from django.shortcuts import render, redirect
from django.contrib import messages
from model_students.models import Student, Teacher, Evaluation, Course, Punctuation

def home(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Verificar si es estudiante
        try:
            student = Student.objects.get(username=username, password=password)
            request.session['user_type'] = 'student'
            request.session['user_id'] = student.ci
            return redirect('dashboard')
        except Student.DoesNotExist:
            pass
        
        # Verificar si es profesor
        try:
            teacher = Teacher.objects.get(username=username, password=password)
            request.session['user_type'] = 'teacher'
            request.session['user_id'] = teacher.ci
            return redirect('dashboard')
        except Teacher.DoesNotExist:
            pass
        
        messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'registration/login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        ci = request.POST['ci']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'registration/register.html')
        
        # Determinar tipo de usuario automáticamente por email
        is_teacher = email.endswith('@profesor.edu') or email.endswith('@teacher.edu') or 'profesor' in email.lower()
        
        try:
            if is_teacher:
                Teacher.objects.create(
                    username=username,
                    name=username,
                    last_name='',
                    ci=ci,
                    email=email,
                    password=password
                )
                messages.success(request, 'Profesor registrado exitosamente')
            else:
                Student.objects.create(
                    username=username,
                    name=username,
                    last_name='',
                    ci=ci,
                    email=email,
                    password=password
                )
                messages.success(request, 'Estudiante registrado exitosamente')
            return redirect('home')
        except:
            messages.error(request, 'Error al registrar usuario. Verifique que el email y cédula no estén en uso')
    
    return render(request, 'registration/register.html')

def dashboard(request):
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    
    # Verificar si el usuario está logueado
    if not user_type or not user_id:
        messages.error(request, 'Debes iniciar sesión para acceder al dashboard')
        return redirect('home')
    
    from django.utils import timezone
    
    if user_type == 'student':
        user_data = Student.objects.get(ci=user_id)
        # Solo puntuaciones del estudiante logueado
        evaluations = Punctuation.objects.filter(student=user_data).select_related('evaluation').order_by('-evaluation__date')
        # Calcular evaluaciones aprobadas (score >= 10)
        approved_evaluations = evaluations.filter(score__gte=10).count()
        # Contar materias del grado del estudiante
        courses_count = Course.objects.filter(grade=user_data.grade).count()
        # Próximas evaluaciones (futuras) del grado del estudiante
        upcoming_evaluations = Evaluation.objects.filter(
            course__grade=user_data.grade,
            date__gt=timezone.now()
        ).order_by('date')[:5]
    else:
        user_data = Teacher.objects.get(ci=user_id)
        # Solo evaluaciones de cursos asignados al profesor
        evaluations = Evaluation.objects.filter(course__teacher=user_data).order_by('-date')
        approved_evaluations = 0
        # Contar materias asignadas al profesor
        courses_count = Course.objects.filter(teacher=user_data).count()
        # Próximas evaluaciones del profesor
        upcoming_evaluations = Evaluation.objects.filter(
            course__teacher=user_data,
            date__gt=timezone.now()
        ).order_by('date')[:5]
    
    return render(request, 'dashboard.html', {
        'user_type': user_type,
        'user_data': user_data,
        'evaluations': evaluations,
        'approved_evaluations': approved_evaluations,
        'courses_count': courses_count,
        'upcoming_evaluations': upcoming_evaluations
    })

def update_evaluations(request):
    # Verificar si el usuario está logueado y es profesor
    user_type = request.session.get('user_type')
    if not user_type or user_type != 'teacher':
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('home')
    
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('score_'):
                eval_id = key.split('_')[1]
                evaluation = Evaluation.objects.get(id=eval_id)
                evaluation.score = value
                evaluation.save()
        
        messages.success(request, 'Puntuaciones actualizadas correctamente')
    
    return redirect('classroom')

def classroom(request):
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    
    if user_type == 'student':
        user_data = Student.objects.get(ci=user_id)
        # Obtener compañeros del mismo grado ordenados por promedio
        from django.db.models import Avg
        students = Student.objects.filter(grade=user_data.grade).annotate(
            promedio=Avg('punctuation__score')
        ).order_by('-promedio')
        evaluations = None
    else:
        user_data = Teacher.objects.get(ci=user_id)
        # Obtener todos los estudiantes y sus puntuaciones
        students = Student.objects.all()
        evaluations = Punctuation.objects.all().select_related('student', 'evaluation__course')
    
    return render(request, 'classroom.html', {
        'user_type': user_type,
        'user_data': user_data,
        'students': students,
        'evaluations': evaluations
    })

def manage_evaluations(request):
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    if not user_type or user_type != 'teacher':
        messages.error(request, 'No tienes permisos para acceder a esta página')
        return redirect('home')
    
    teacher = Teacher.objects.get(ci=user_id)
    courses = Course.objects.filter(teacher=teacher)
    evaluations = Evaluation.objects.filter(course__teacher=teacher).order_by('-date')
    
    return render(request, 'manage_evaluations.html', {
        'user_type': user_type,
        'user_data': teacher,
        'teacher': teacher,
        'courses': courses,
        'evaluations': evaluations
    })

def create_evaluation(request):
    # Verificar si el usuario es profesor
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    if not user_type or user_type != 'teacher':
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            teacher = Teacher.objects.get(ci=user_id)
            course_id = request.POST['course_id']
            course = Course.objects.get(id=course_id, teacher=teacher)
            
            # Crear evaluación para todos los estudiantes (sin asignar estudiante específico)
            # Los estudiantes verán la evaluación disponible para su materia
            Evaluation.objects.create(
                date=request.POST['date'],
                subject=request.POST['subject'],
                type=request.POST['type'],
                score=0,  # Puntuación inicial 0, se actualizará después
                course=course,
                student=None  # Sin estudiante específico
            )
            messages.success(request, f'Evaluación creada para la materia {course.name_course}')
        except Exception as e:
            messages.error(request, 'Error al crear la evaluación')
    
    return redirect('manage_evaluations')

def delete_evaluation(request, eval_id):
    # Verificar si el usuario es profesor
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    if not user_type or user_type != 'teacher':
        messages.error(request, 'No tienes permisos para realizar esta acción')
        return redirect('home')
    
    try:
        teacher = Teacher.objects.get(ci=user_id)
        evaluation = Evaluation.objects.get(id=eval_id, course__teacher=teacher)
        evaluation.delete()
        messages.success(request, 'Evaluación eliminada exitosamente')
    except:
        messages.error(request, 'Error al eliminar la evaluación')
    
    return redirect('manage_evaluations')

def profile(request):
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    
    if not user_type or not user_id:
        return redirect('home')
    
    if user_type == 'student':
        user_data = Student.objects.get(ci=user_id)
    else:
        user_data = Teacher.objects.get(ci=user_id)
    
    return render(request, 'profile.html', {
        'user_type': user_type,
        'user_data': user_data
    })

def settings(request):
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    
    if not user_type or not user_id:
        return redirect('home')
    
    if user_type == 'student':
        user_data = Student.objects.get(ci=user_id)
    else:
        user_data = Teacher.objects.get(ci=user_id)
    
    return render(request, 'settings.html', {
        'user_type': user_type,
        'user_data': user_data})
    
def my_subjects(request):
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    
    # Solo estudiantes pueden acceder
    if user_type != 'student':
        messages.error(request, 'Acceso denied')
        return redirect('dashboard')
    
    user_data = Student.objects.get(ci=user_id)
    
    # Obtener todas las materias del grado del estudiante
    all_courses = Course.objects.filter(grade=user_data.grade)
    
    # Obtener puntuaciones del estudiante
    punctuations = Punctuation.objects.filter(student=user_data).select_related('evaluation__course')
    
    # Inicializar datos de materias
    subjects_data = {}
    total_score = 0
    total_count = 0
    
    # Crear entrada para todas las materias del grado
    for course in all_courses:
        subjects_data[course.name_course] = {
            'course': course,
            'scores': [],
            'evaluations': [],
            'average': 0
        }
    
    # Agregar puntuaciones existentes
    for punctuation in punctuations:
        course_name = punctuation.evaluation.course.name_course
        if course_name in subjects_data:
            subjects_data[course_name]['scores'].append(float(punctuation.score))
            subjects_data[course_name]['evaluations'].append(punctuation.evaluation)
            total_score += float(punctuation.score)
            total_count += 1
            # Debug: imprimir información
            print(f"Materia: {course_name}, Nota: {punctuation.score}, Evaluación: {punctuation.evaluation.subject}")
    
    # Calcular promedios
    for subject in subjects_data.values():
        if subject['scores']:
            subject['average'] = sum(subject['scores']) / len(subject['scores'])
    
    overall_average = total_score / total_count if total_count > 0 else 0
    
    return render(request, 'my_subjects.html', {
        'user_type': user_type,
        'user_data': user_data,
        'subjects_data': subjects_data,
        'overall_average': overall_average
    })

def subject_detail(request, subject_name):
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    
    if user_type != 'student':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    user_data = Student.objects.get(ci=user_id)
    
    # Obtener el curso específico
    try:
        course = Course.objects.get(name_course=subject_name, grade=user_data.grade)
    except Course.DoesNotExist:
        messages.error(request, 'Materia no encontrada')
        return redirect('my_subjects')
    
    # Obtener puntuaciones del estudiante para esta materia
    punctuations = Punctuation.objects.filter(
        student=user_data,
        evaluation__course=course
    ).select_related('evaluation').order_by('evaluation__date')
    
    # Calcular promedio
    scores = [float(p.score) for p in punctuations]
    average = sum(scores) / len(scores) if scores else 0
    
    return render(request, 'subject_detail.html', {
        'user_type': user_type,
        'user_data': user_data,
        'subject_name': subject_name,
        'course': course,
        'punctuations': punctuations,
        'average': average
    })

def logout_view(request):
    request.session.flush()
    return redirect('home') 