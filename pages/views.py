from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import models
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
        # Calcular total de estudiantes únicos en los grados de las materias del profesor
        teacher_courses = Course.objects.filter(teacher=user_data)
        total_students = Student.objects.filter(grade__in=teacher_courses.values('grade')).distinct().count()
        # Próximas evaluaciones del profesor
        upcoming_evaluations = Evaluation.objects.filter(
            course__teacher=user_data,
            date__gt=timezone.now()
        ).order_by('date')[:5]
    
    context = {
        'user_type': user_type,
        'user_data': user_data,
        'evaluations': evaluations,
        'approved_evaluations': approved_evaluations,
        'courses_count': courses_count,
        'upcoming_evaluations': upcoming_evaluations
    }
    
    # Agregar total_students solo para profesores
    if user_type == 'teacher':
        context['total_students'] = total_students
    
    return render(request, 'dashboard.html', context)

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
        from django.db.models import Avg
        students = Student.objects.filter(grade=user_data.grade).annotate(
            promedio=Avg('punctuation__score')
        ).order_by('-promedio')
        return render(request, 'classroom.html', {
            'user_type': user_type,
            'user_data': user_data,
            'students': students
        })
    else:
        teacher = Teacher.objects.get(ci=user_id)
        
        # Obtener materias del profesor
        teacher_courses = Course.objects.filter(teacher=teacher)
        
        # Estadísticas generales
        from django.db.models import Avg, Count
        total_students = Student.objects.filter(grade__in=teacher_courses.values('grade')).distinct().count()
        total_evaluations = Evaluation.objects.filter(course__teacher=teacher).count()
        
        # Estudiantes por materia con promedios
        courses_data = []
        for course in teacher_courses:
            students = Student.objects.filter(grade=course.grade).annotate(
                promedio=Avg('punctuation__score', filter=models.Q(punctuation__evaluation__course=course))
            ).order_by('name', 'last_name')
            
            # Evaluaciones recientes de la materia
            recent_evaluations = Evaluation.objects.filter(course=course).order_by('-date')[:3]
            
            courses_data.append({
                'course': course,
                'students': students,
                'students_count': students.count(),
                'recent_evaluations': recent_evaluations
            })
        
        # Evaluaciones pendientes de calificar
        from django.utils import timezone
        pending_evaluations = []
        for course in teacher_courses:
            evaluations = Evaluation.objects.filter(course=course)
            for evaluation in evaluations:
                students_count = Student.objects.filter(grade=course.grade).count()
                graded_count = Punctuation.objects.filter(evaluation=evaluation).count()
                if graded_count < students_count:
                    pending_evaluations.append({
                        'evaluation': evaluation,
                        'pending_count': students_count - graded_count,
                        'total_count': students_count
                    })
        
        return render(request, 'classroom.html', {
            'user_type': user_type,
            'user_data': teacher,
            'courses_data': courses_data,
            'total_students': total_students,
            'total_evaluations': total_evaluations,
            'pending_evaluations': pending_evaluations[:5]  # Solo las 5 más recientes
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
            
            # Crear evaluación
            Evaluation.objects.create(
                date=request.POST['date'],
                subject=request.POST['subject'],
                type=request.POST['type'],
                course=course
            )
            messages.success(request, f'Evaluación creada para la materia {course.name_course}')
        except Exception as e:
            messages.error(request, f'Error al crear la evaluación: {str(e)}')
    
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

def grade_evaluation(request, eval_id):
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    
    if user_type != 'teacher':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    teacher = Teacher.objects.get(ci=user_id)
    evaluation = Evaluation.objects.get(id=eval_id, course__teacher=teacher)
    
    # Obtener estudiantes del grado de la materia
    students = Student.objects.filter(grade=evaluation.course.grade).order_by('name', 'last_name')
    
    if request.method == 'POST':
        for student in students:
            score_key = f'score_{student.ci}'
            if score_key in request.POST and request.POST[score_key]:
                score = float(request.POST[score_key])
                # Crear o actualizar puntuación
                punctuation, created = Punctuation.objects.get_or_create(
                    evaluation=evaluation,
                    student=student,
                    defaults={'score': score}
                )
                if not created:
                    punctuation.score = score
                    punctuation.save()
        
        messages.success(request, 'Notas registradas correctamente')
        return redirect('manage_evaluations')
    
    # Obtener puntuaciones existentes y agregar a estudiantes
    punctuations = Punctuation.objects.filter(evaluation=evaluation)
    scores_dict = {p.student.ci: p.score for p in punctuations}
    
    # Agregar score a cada estudiante
    students_with_scores = []
    for student in students:
        student.current_score = scores_dict.get(student.ci, '')
        students_with_scores.append(student)
    
    return render(request, 'grade_evaluation.html', {
        'user_type': user_type,
        'user_data': teacher,
        'evaluation': evaluation,
        'students': students_with_scores
    })

def student_reports(request):
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    
    if user_type != 'teacher':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    teacher = Teacher.objects.get(ci=user_id)
    
    # Obtener estudiantes de los grados de las materias del profesor
    teacher_courses = Course.objects.filter(teacher=teacher)
    students = Student.objects.filter(grade__in=teacher_courses.values('grade')).distinct().order_by('name', 'last_name')
    
    return render(request, 'student_reports.html', {
        'user_type': user_type,
        'user_data': teacher,
        'students': students
    })

def generate_student_report(request, student_ci):
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    
    if user_type != 'teacher':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    teacher = Teacher.objects.get(ci=user_id)
    student = Student.objects.get(ci=student_ci)
    
    # Obtener materias del grado del estudiante
    courses = Course.objects.filter(grade=student.grade)
    
    # Obtener calificaciones del estudiante
    report_data = []
    total_score = 0
    total_count = 0
    
    for course in courses:
        punctuations = Punctuation.objects.filter(
            student=student,
            evaluation__course=course
        ).select_related('evaluation')
        
        scores = [float(p.score) for p in punctuations]
        average = sum(scores) / len(scores) if scores else 0
        
        if scores:
            total_score += average
            total_count += 1
        
        report_data.append({
            'course': course,
            'punctuations': punctuations,
            'average': average,
            'status': 'Aprobado' if average >= 10 else 'Reprobado'
        })
    
    overall_average = total_score / total_count if total_count > 0 else 0
    
    if request.GET.get('pdf'):
        from django.http import HttpResponse
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="boletin_{student.name}_{student.last_name}.pdf"'
        
        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter
        
        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, "ThinkIt - Sistema Académico")
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, height - 80, "BOLETÍN DE CALIFICACIONES")
        
        # Student info
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 120, f"Estudiante: {student.name} {student.last_name}")
        p.drawString(50, height - 140, f"Cédula: {student.ci}")
        p.drawString(50, height - 160, f"Grado: {student.grade}")
        p.drawString(50, height - 180, f"Promedio General: {overall_average:.2f}")
        
        # Table header
        y = height - 220
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y, "MATERIA")
        p.drawString(200, y, "PROMEDIO")
        p.drawString(300, y, "ESTADO")
        
        # Table content
        p.setFont("Helvetica", 10)
        y -= 20
        for data in report_data:
            p.drawString(50, y, data['course'].name_course)
            p.drawString(200, y, f"{data['average']:.2f}")
            p.drawString(300, y, data['status'])
            y -= 20
        
        p.showPage()
        p.save()
        return response
    
    return render(request, 'student_report_detail.html', {
        'user_type': user_type,
        'user_data': teacher,
        'student': student,
        'report_data': report_data,
        'overall_average': overall_average
    })

def teacher_subjects(request):
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    
    # Solo profesores pueden acceder
    if user_type != 'teacher':
        messages.error(request, 'Acceso denegado')
        return redirect('dashboard')
    
    teacher = Teacher.objects.get(ci=user_id)
    
    # Obtener materias asignadas al profesor
    courses = Course.objects.filter(teacher=teacher).order_by('grade', 'name_course')
    
    # Obtener estadísticas por materia
    subjects_data = []
    for course in courses:
        # Contar estudiantes del grado
        students_count = Student.objects.filter(grade=course.grade).count()
        
        # Contar evaluaciones de la materia
        evaluations_count = Evaluation.objects.filter(course=course).count()
        
        # Calcular promedio general de la materia
        from django.db.models import Avg
        avg_score = Punctuation.objects.filter(
            evaluation__course=course
        ).aggregate(avg=Avg('score'))['avg'] or 0
        
        # Próxima evaluación
        from django.utils import timezone
        next_evaluation = Evaluation.objects.filter(
            course=course,
            date__gt=timezone.now()
        ).order_by('date').first()
        
        subjects_data.append({
            'course': course,
            'students_count': students_count,
            'evaluations_count': evaluations_count,
            'average_score': round(avg_score, 2),
            'next_evaluation': next_evaluation
        })
    
    return render(request, 'teacher_subjects.html', {
        'user_type': user_type,
        'user_data': teacher,
        'subjects_data': subjects_data,
        'total_courses': len(subjects_data)
    })

def logout_view(request):
    request.session.flush()
    return redirect('home') 