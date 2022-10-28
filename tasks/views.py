from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request,'home.html')

def signup(request):
    if request.method == 'GET':
        return render(request,'signup.html',{'form':UserCreationForm})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request,user)
                return redirect('tasks')
            except IntegrityError:
                return render(request,'signup.html',{'form':UserCreationForm,'error':'El usuario ya existe'}) 
        return render(request,'signup.html',{'form':UserCreationForm,'error':"Password doesn't match"})

@login_required
def tasks(request):
    taskss = Task.objects.filter(user = request.user,datecompleted__isnull=True)
    return render(request,'tasks.html',{'tasks':taskss,'title':'Tasks Pending'})
@login_required
def new_task(request):
    if request.method == 'GET':
        return render(request,'create_task.html',{'form':TaskForm})
    else:
        #print(request.POST)
        #return redirect('newtask')
        # form = TaskForm(request.POST)
        # print(form)
        # return render(request,'create_task.html',{'form':TaskForm})
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request,'create_task.html',{'form':TaskForm,'error':'Por favor proporciona datos válidos'})
            
@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect('home') 

def autenticar(request):
    if request.method == 'GET':
        return render(request,'signin.html',{'form':AuthenticationForm})
    else:
        user = authenticate(request,username=request.POST['username'],password=request.POST['password'])
        if user == None:
            return render(request, 'signin.html',{'form':AuthenticationForm,'error':'Usuario o contraseña incorrectos'})
        else:
            login(request,user)
            return redirect('tasks')
@login_required
def task_detail(request,task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user= request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task,pk=task_id, user=request.user)
            form = TaskForm(request.POST,instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request,'task_detail.html',{'task':task,'form':form,'error':'Error actualizando valores'})
@login_required
def complete_task(request,task_id):
    task = get_object_or_404(Task,pk=task_id,user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')
@login_required
def delete_task(request,task_id):
    task = get_object_or_404(Task,pk=task_id,user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

@login_required
def tasks_completed(request):
    taskss = Task.objects.filter(user = request.user,datecompleted__isnull=False)
    return render(request,'tasks.html',{'tasks':taskss,'title':'Tasks Completed'})