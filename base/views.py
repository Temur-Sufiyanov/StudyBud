from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Room, Topic, Massage, User
from .forms import RoomForm, UserForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .forms import MyusercreationForm


def loginPage(request):
    page = 'login_page'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exist!")
            
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request,user)
            messages.success(request, 'You have logged successfuly!')
            return redirect('home')
        else:
            messages.error(request, "Username OR Password does not exist!")
    context = {
        'page':page,
    }
    return render(request, 'base/login_register.html', context)

def registerUser(request):
    form = MyusercreationForm()
    
    if request.method == 'POST':
        form = MyusercreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            messages.success(request, 'You succesfully registred and logged!')
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')
    context ={
        'form':form,
    }
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains = q) | Q(name__icontains=q) | Q(descriptiom__icontains=q))
    topics = Topic.objects.all()[0:3]
    room_messages = Massage.objects.filter(room__topic__name__icontains=q)
    context = {
        'rooms':rooms,
        'topics':topics,
        'rooms_count': rooms.count(),
        'room_messages':room_messages,
    }
    return render(request, 'base/home.html', context)

def room(request,pk):
    room = Room.objects.get(id=pk)
    room_messages = room.massage_set.all()
    participants = room.participants.all()
    
    if request.method == 'POST':
        message = Massage.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {
        'room': room,
        'room_messages':room_messages,
        'participants':participants,
    }
    return render(request, 'base/room.html', context)

@login_required(login_url='/login')
def createRoom(request):
    current_url = request.build_absolute_uri()
    
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            descriptiom = request.POST.get('room_about'),
        )
        return redirect('home')
    context = {
        'form':form,
        'topics':topics,
        'current_url':current_url,
    }
    return render(request, 'base/room_form.html', context)

@login_required(login_url='/login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    
    if request.user != room.host:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.descriptiom = request.POST.get('room_about')
        room.save()
        return redirect('home')
    context  = {
        'form':form,
        'topics':topics,
        'room':room,
    }
    
    return render(request, 'base/room_form.html', context)

@login_required(login_url='/login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    
    return render(request, 'base/delete.html', {'obj':room})


@login_required(login_url='/login')
def deleteMessage(request, pk):
    message = Massage.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    
    return render(request, 'base/delete.html', {'obj':message})

def userProfile(request,pk):
    user = User.objects.get(id=pk)
    room = user.room_set.all()
    room_messages = user.massage_set.all()
    topics = Topic.objects.all()
    context = {
        'user':user,
        'rooms':room,
        'room_messages':room_messages,
        'topics':topics,
    }
    return render(request, 'base/profile.html', context)

@login_required(login_url='/login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES,  instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=user.id)
    context = {
        'form':form,
    }
    return render(request, 'base/update-user.html', context)


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics':topics})


def activityPage(request):
    messages = Massage.objects.all()
    context = {
        'messages':messages,
    }
    return render(request, 'base/activity.html', context)