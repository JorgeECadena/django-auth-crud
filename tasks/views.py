from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm 
from .models import CustomUserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError 
from .forms import TaskForm
from .models import Task
from django.utils import timezone

# Create your views here.
def home(request):
    return render(request, 'home.html')

def signup(request):
    # When page is being accessed by GET method,
    # return form
    if(request.method == 'GET'):
        return render(request, 'signup.html', {
            'form': CustomUserCreationForm(),
        })
    # Validate form responses
    else:
        # Check if both provided passwords are the same
        if(request.POST['password1'] == request.POST['password2']):
            # Validate the provided password
            try:
               validate_password(request.POST['password1'])
            except ValidationError as e:
                return render(request, 'signup.html', {
                    'form': CustomUserCreationForm(),
                    'invalidPassword': True,
                    'error': e,
                })

            # Validate if user is already registered
            try:
                user = User.objects.create_user(username=request.POST['username'], 
                password=request.POST['password1'])
                user.save()
                return redirect('signin') 
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': CustomUserCreationForm(),
                    'error': 'Username already exists'
                })
        else:
            return render(request, 'signup.html', {
                'form': CustomUserCreationForm(),
                'error': 'Passwords do not match',
            })

@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    # When page is being accessed by GET method
    # return form
    if(request.method == 'GET'):
        return render(request, 'signin.html', {
            'form': AuthenticationForm,
        })
    else:
        user = authenticate(request, username=request.POST['username'],
                            password=request.POST['password'])
        if(not user):
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'The provided credentials do not exist! Please, try again'
            })
        else:
            login(request, user)
            return redirect('home')

@login_required
def tasks(request):
    if request.method == 'GET':
        tasks = Task.objects.filter(user=request.user, completiondate__isnull=True)
        return render(request, 'tasks.html', {
            'tasks': tasks,
            'btn_name': 'Show completed tasks',
        })
    else:
        return redirect('completed_tasks')

@login_required
def completed_tasks(request):
    if request.method == 'GET':
        tasks = Task.objects.filter(user=request.user, completiondate__isnull=False)
        tasks = tasks.order_by('-completiondate')
        return render(request, 'tasks.html', {
            'tasks': tasks,
            'btn_name': 'Show uncompleted tasks',
        })
    else:
        return redirect('tasks')

@login_required
def create_task(request):
    if (request.method == 'GET'):
        return render(request, 'create_task.html', {
            'form': TaskForm,
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm,
                'error': 'Please provide valid information',
            })

@login_required
def task_details(request, task_id):
    if(request.method == 'GET'):
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_details.html', {
            'task': task,
            'form': form,
        })
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_details.html', {
                'task': task,
                'form': form,
                'error': 'Please provide valid information',
            })

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if(request.method == 'POST'):
        task.completiondate = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if(request.method == 'POST'):
        task.delete()
        return redirect('tasks')
