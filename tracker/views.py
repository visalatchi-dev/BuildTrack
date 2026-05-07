from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from .models import Project, Worker, DailyLog, Issue

def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'tracker/landing.html')

def login_view(request):
    error = ''
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        login_role = request.POST.get('login_role', 'worker')
        user = authenticate(request, username=username, password=password)
        if user:
            if login_role == 'admin' and not user.is_superuser:
                error = 'You are not an Admin!'
            elif login_role == 'supervisor' and not user.groups.filter(name='Supervisor').exists():
                error = 'You are not a Supervisor!'
            elif login_role == 'worker' and not user.groups.filter(name='Worker').exists():
                error = 'You are not a Worker!'
            else:
                login(request, user)
                return redirect('dashboard')
        else:
            error = 'Invalid username or password!'
    return render(request, 'tracker/login.html', {'error': error})

def logout_view(request):
    logout(request)
    return redirect('login')

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    user = request.user
    is_admin = user.is_superuser
    is_supervisor = user.groups.filter(name='Supervisor').exists()
    is_worker = user.groups.filter(name='Worker').exists()

    if is_admin:
        projects = Project.objects.all()
        issues = Issue.objects.all()
        workers = Worker.objects.all()
        logs = DailyLog.objects.all()
    
    elif is_supervisor:
        # Supervisor own project irunthu kaanum, illana all projects
        worker_profile = Worker.objects.filter(user=user).first()
        if worker_profile and worker_profile.project:
            projects = Project.objects.filter(id=worker_profile.project.id)
            issues = Issue.objects.filter(project=worker_profile.project)
            workers = Worker.objects.filter(project=worker_profile.project)
            logs = DailyLog.objects.filter(project=worker_profile.project)
        else:
            # Worker profile illana all projects kaatum
            projects = Project.objects.all()
            issues = Issue.objects.all()
            workers = Worker.objects.all()
            logs = DailyLog.objects.all()
    elif is_worker:
        worker_profile = Worker.objects.filter(user=user).first()
        if worker_profile and worker_profile.project:
            projects = Project.objects.filter(id=worker_profile.project.id)
            issues = Issue.objects.filter(project=worker_profile.project)
            workers = Worker.objects.filter(project=worker_profile.project)
            logs = DailyLog.objects.filter(project=worker_profile.project)
        else:
            projects = Project.objects.all()
            issues = Issue.objects.all()
            workers = Worker.objects.all()
            logs = DailyLog.objects.all()
    return render(request, 'tracker/dashboard.html', {
        'projects': projects,
        'issues': issues,
        'workers': workers,
        'logs': logs,
        'is_admin': is_admin,
        'is_supervisor': is_supervisor,
        'is_worker': is_worker,
    })
def daily_log(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    user = request.user
    is_admin = user.is_superuser
    is_supervisor = user.groups.filter(name='Supervisor').exists()
    is_worker = user.groups.filter(name='Worker').exists()
    logs = DailyLog.objects.none()
    projects = Project.objects.none()
    if request.method == 'POST':
        DailyLog.objects.create(
            project_id=request.POST['project'],
            activity=request.POST['activity'],
            status=request.POST['status'],
            logged_by=request.user
        )
        return redirect('daily_log')
    if is_admin:
        logs = DailyLog.objects.all().order_by('-date')
        projects = Project.objects.all()
    elif is_supervisor:
        worker_profile = Worker.objects.filter(user=user).first()
        if worker_profile and worker_profile.project:
            logs = DailyLog.objects.filter(project=worker_profile.project).order_by('-date')
            projects = Project.objects.all()
    elif is_worker:
        worker_profile = Worker.objects.filter(user=user).first()
        if worker_profile and worker_profile.project:
            logs = DailyLog.objects.filter(project=worker_profile.project).order_by('-date')
            projects = Project.objects.all()
    logs_done = logs.filter(status='done').count()
    logs_partial = logs.filter(status='partial').count()
    logs_issue = logs.filter(status='issue').count()
    return render(request, 'tracker/daily_log.html', {
        'logs': logs,
        'projects': projects,
        'logs_done': logs_done,       
        'logs_partial': logs_partial, 
        'logs_issue': logs_issue,
        'is_admin': is_admin
    })
def delete_log(request, log_id):
    if not request.user.is_authenticated:
        return redirect('/login/')
    if not request.user.is_superuser:
        return redirect('/daily-log/')
    log = get_object_or_404(DailyLog, id=log_id)
    log.delete()
    return redirect('daily_log')

def issues(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    user = request.user
    is_admin = user.is_superuser
    is_supervisor = user.groups.filter(name='Supervisor').exists()
    is_worker = user.groups.filter(name='Worker').exists()

    if request.method == 'POST':
        Issue.objects.create(
            project_id=request.POST['project'],
            description=request.POST['description'],
            priority=request.POST['priority'],
            assigned_to=request.POST.get('assigned_to', ''),
            reported_by=request.user
        )
        return redirect('issues')

    if is_admin:
        all_issues = Issue.objects.all().order_by('-created_at')
        projects = Project.objects.all()
    elif is_supervisor:
        worker_profile = Worker.objects.filter(user=user).first()
        if worker_profile and worker_profile.project:
            all_issues = Issue.objects.filter(project=worker_profile.project).order_by('-created_at')
            projects = Project.objects.all()
    elif is_worker:
        worker_profile = Worker.objects.filter(user=user).first()
        if worker_profile and worker_profile.project:
            all_issues = Issue.objects.filter(project=worker_profile.project).order_by('-created_at')
            projects = Project.objects.all()

    return render(request, 'tracker/issues.html', {
        'issues': all_issues,
        'projects': projects,
        'is_admin': is_admin,
        'is_supervisor': is_supervisor,
        'is_worker': is_worker,
        'issues_high':   all_issues.filter(priority='high').count(),    # ← ADD
        'issues_medium': all_issues.filter(priority='medium').count(),  # ← ADD
        'issues_low':    all_issues.filter(priority='low').count(),     # ← ADD
    })

def workers(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    user = request.user
    is_admin = user.is_superuser
    is_supervisor = user.groups.filter(name='Supervisor').exists()
    is_worker = user.groups.filter(name='Worker').exists()
    if is_admin:
        all_workers = Worker.objects.all()
        present_count = all_workers.filter(is_present=True).count()
        absent_count = all_workers.filter(is_present=False).count()
    elif is_supervisor:
        worker_profile = Worker.objects.filter(user=user).first()
        if worker_profile and worker_profile.project:
            all_workers = Worker.objects.filter(project=worker_profile.project)
            present_count = all_workers.filter(is_present=True).count()
            absent_count = all_workers.filter(is_present=False).count()
    elif is_worker:
        worker_profile = Worker.objects.filter(user=user).first()
        if worker_profile and worker_profile.project:
            all_workers = Worker.objects.filter(project=worker_profile.project)
            present_count = all_workers.filter(is_present=True).count()
            absent_count = all_workers.filter(is_present=False).count()
    is_admin = request.user.is_superuser
    is_supervisor = request.user.groups.filter(name='Supervisor').exists()
    return render(request, 'tracker/workers.html', {
        'workers': all_workers,
        'present_count': present_count,
        'absent_count': absent_count,
        'is_admin': is_admin,
        'is_supervisor': is_supervisor,
    })

def bulk_attendance(request):
    user = request.user
    is_admin = user.is_superuser
    is_supervisor = user.groups.filter(name='Supervisor').exists()
    is_worker = user.groups.filter(name='Worker').exists()
    if request.method == 'POST':
        for worker in Worker.objects.all():
            # Inga "worker_{{ worker.id }}" nu name kuduthurukkom
            status = request.POST.get(f'worker_{worker.id}')
            
            # Debugging: status varudha nu paaka print pannunga
            print(f"Worker: {worker.name}, Status: {status}") 
            
            if status == 'present':
                worker.is_present = True
            else:
                worker.is_present = False
            worker.save()
        return redirect('workers')
    if is_admin:
        workers = Worker.objects.all()
    elif is_supervisor:
        worker_profile = Worker.objects.filter(user=user).first()
        if worker_profile and worker_profile.project:
            workers = Worker.objects.filter(project=worker_profile.project)
    elif is_worker:
        worker_profile = Worker.objects.filter(user=user).first()
        if worker_profile and worker_profile.project:
            workers = Worker.objects.filter(project=worker_profile.project)
    return render(request, 'tracker/bulk_attendance.html', {'workers': workers})
def project_add(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    if request.method == 'POST':
        Project.objects.create(
            name=request.POST['name'],
            status=request.POST['status'],
            deadline=request.POST['deadline'],
            completion=request.POST.get('completion', 0),
            workers_count=request.POST.get('workers_count', 0),
        )
        return redirect('dashboard')
    return render(request, 'tracker/project_form.html', {'action': 'Add'})

def project_edit(request, pk):
    if not request.user.is_authenticated:
        return redirect('/login/')
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.name = request.POST['name']
        project.status = request.POST['status']
        project.deadline = request.POST['deadline']
        project.completion = request.POST.get('completion', 0)
        project.workers_count = request.POST.get('workers_count', 0)
        project.save()
        return redirect('dashboard')
    return render(request, 'tracker/project_form.html', {
        'action': 'Edit',
        'project': project
    })

def project_delete(request, pk):
    if not request.user.is_authenticated:
        return redirect('/login/')
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    return redirect('dashboard')
def worker_delete(request, pk):
    if not request.user.is_authenticated:
        return redirect('/login/')
    worker = get_object_or_404(Worker, pk=pk)
    worker.delete()
    return redirect('workers')

def issue_delete(request, pk):
    if not request.user.is_authenticated:
        return redirect('/login/')
    issue = get_object_or_404(Issue, pk=pk)
    issue.delete()
    return redirect('issues')
def user_delete(request, pk):
    if not request.user.is_authenticated:
        return redirect('/login/')
    if not request.user.is_superuser:
        return redirect('dashboard')
    user = get_object_or_404(User, pk=pk)
    user.delete()
    return redirect('users_list')
from .models import Project   # 🔥 top la add pannunga

def users_list(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    if not request.user.is_superuser:
        return redirect('dashboard')

    users = User.objects.filter(is_superuser=False).order_by('-date_joined')
    projects = Project.objects.all()   

    return render(request, 'tracker/users_list.html', {
        'users': users,
        'projects': projects  
    })

def user_promote(request, pk):
    if not request.user.is_authenticated:
        return redirect('/login/')
    if not request.user.is_superuser:
        return redirect('dashboard')
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        role = request.POST.get('role')
        user.groups.clear()
        if role != 'Viewer':
            group = Group.objects.get_or_create(name=role)[0]
            user.groups.add(group)
        user.save()
    return redirect('users_list')

def user_add(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    if not request.user.is_superuser:
        return redirect('dashboard')

    error = ''
    projects = Project.objects.all()

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']
        worker_name = request.POST.get('worker_name', username)
        project_id = request.POST.get('project')
        is_present = request.POST.get('is_present') == 'on'

        if User.objects.filter(username=username).exists():
            error = 'Username already taken!'
        else:
            user = User.objects.create_user(username=username, password=password)

            # GROUP ADD
            if role != 'Viewer':
                group = Group.objects.get_or_create(name=role)[0]
                user.groups.add(group)

            # 🔥 IMPORTANT FIX HERE
            if role in ['Worker', 'Supervisor']:
                if not project_id:
                    error = "Project select pannunga!"
                else:
                    Worker.objects.create(
                        user=user,
                        name=worker_name,
                        role=role,
                        project_id=project_id,
                        is_present=is_present
                    )

            return redirect('users_list')

    return render(request, 'tracker/user_add.html', {
        'error': error,
        'projects': projects
    })
def user_edit(request, pk):
    if not request.user.is_authenticated:
        return redirect('/login/')
    if not request.user.is_superuser:
        return redirect('dashboard')

    edit_user = get_object_or_404(User, pk=pk)
    error = ''

    if request.method == 'POST':
        new_username = request.POST.get('username', '').strip()
        new_password = request.POST.get('password', '').strip()
        role = request.POST.get('role')
        project_id = request.POST.get('project')

        # Username update
        if new_username and new_username != edit_user.username:
            if User.objects.filter(username=new_username).exists():
                error = 'Username already taken!'
            else:
                edit_user.username = new_username

        # Password update
        if new_password:
            edit_user.set_password(new_password)

        if not error:
            edit_user.save()

            # ✅ ROLE UPDATE
            if role:
                edit_user.groups.clear()
                group = Group.objects.get(name=role)
                edit_user.groups.add(group)

            # ✅ PROJECT UPDATE
            try:
                worker = Worker.objects.get(user=edit_user)
                if project_id:
                    worker.project_id = project_id
                else:
                    worker.project = None
                worker.save()
            except Worker.DoesNotExist:
                pass

            return redirect('users_list')

    return render(request, 'tracker/user_edit.html', {
        'edit_user': edit_user,
        'error': error
    })