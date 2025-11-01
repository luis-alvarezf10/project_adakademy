from django.shortcuts import render, redirect
from django.contrib import messages
from model_students.models import Student, Teacher, Evaluation, Course

def home(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Verificar si es estudiante
        try:
            student = Student.objects.get(name_student=username, password=password)
            request.session['user_type'] = 'student'
            request.session['user_id'] = student.ci
            return redirect('dashboard')
        except Student.DoesNotExist:
            pass
        
        # Verificar si es profesor
        try:
            teacher = Teacher.objects.get(name_teacher=username, password=password)
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
                    name_teacher=username,
                    ci=ci,
                    email=email,
                    password=password
                )
                messages.success(request, 'Profesor registrado exitosamente')
            else:
                Student.objects.create(
                    name_student=username,
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
    
    if user_type == 'student':
        user_data = Student.objects.get(ci=user_id)
        # Solo evaluaciones del estudiante logueado
        evaluations = Evaluation.objects.filter(student=user_data).order_by('-date')
    else:
        user_data = Teacher.objects.get(ci=user_id)
        # Solo evaluaciones de cursos asignados al profesor
        evaluations = Evaluation.objects.filter(course__teacher=user_data).order_by('-date')
    
    return render(request, 'dashboard.html', {
        'user_type': user_type,
        'user_data': user_data,
        'evaluations': evaluations
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
        # Obtener todos los estudiantes para mostrar compañeros
        students = Student.objects.all()
        evaluations = None
    else:
        user_data = Teacher.objects.get(ci=user_id)
        # Obtener todos los estudiantes y sus evaluaciones
        students = Student.objects.all()
        evaluations = Evaluation.objects.all().select_related('student', 'course')
    
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

def logout_view(request):
    request.session.flush()
    return redirect('home') 