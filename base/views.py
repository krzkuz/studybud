from unicodedata import name
from django.shortcuts import redirect, render
from django.db.models import Q
from base.forms import RoomForm, MessageForm, UserForm, MyUserCreationForm
from .models import Message, Room, Topic, User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# Create your views here.


def home(request):
    q = request.GET.get('q')
    topics = Topic.objects.all()
    all_rooms = Room.objects.all().count()
    if q :
        rooms = Room.objects.filter(
            Q(topic__name__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q)
            )
        recent_messages = Message.objects.filter(Q(room__topic__name__icontains=q)).order_by('-updated')[:5]
    else:
        rooms = Room.objects.all()
        recent_messages = Message.objects.all().order_by('-updated')[:5]
    context = {
        'topics': topics,
        'rooms': rooms,
        'recent_messages': recent_messages,
        'all_rooms': all_rooms

    }
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    if request.method == 'POST':
        room_message = Message.objects.create(
            body=request.POST.get('body'),
            user=request.user,
            room=room
        )
        room.participants.add(request.user)
        return redirect('room', pk)
           
    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants,
    }
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':        
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room = Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'), 
        )
        return redirect('home')

    context = {
        'form': form,
        'topics': topics,
        }    
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.topic = topic
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {
        'form': form,
        'topics': topics,
        'room': room,
        }  
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("You are not allowed here")
    if request.method == 'POST':
        Room.objects.filter(id=pk).delete()
        return redirect('home')

    context = {'obj': room}
    return render(request, 'base/delete_form.html', context)

def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        
        else:
            messages.error(request, 'Username or password is incorrect')
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logout_page(request):
    logout(request)
    return redirect('home')
    
def register(request):
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    context = {
        'form': form
        }
    return render(request, 'base/login_register.html', context)

@login_required(login_url='login')
def delete_message(request, pk, key):
    message = Message.objects.get(id=pk)
    room_id = message.room.id
    message.delete()
    if key == 1:
        return redirect('room', pk=room_id)
    elif key == 2:
        return redirect('activity_mobile')
    else:
        return redirect('home')


def profile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        'user': user,
        'rooms': rooms,
        'recent_messages': room_messages,
        'topics': topics,
    }
    return render(request, 'base/profile.html', context)
    
@login_required(login_url='login')
def settings(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        print(request.POST)
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=request.user.id)
    context = {'form': form}
    return render(request, 'base/settings.html', context)


def topics_mobile(request):
    topics = Topic.objects.all()
    all_rooms = Room.objects.all().count()
    context = {
        'topics': topics,
        'all_rooms': all_rooms,
        }
    return render(request, 'base/topics_mobile.html', context)


def activity_mobile(request):
    # topics = Topic.objects.all()
    # all_rooms = Room.objects.all().count()
    recent_messages = Message.objects.all().order_by('-updated')[:5] 
    context = {
        'messages': recent_messages
        # 'topics': topics,
        # 'all_rooms': all_rooms,
        }
    return render(request, 'base/activity_mobile.html', context)

# def create_message(request, pk):
#     form = MessageForm()
#     if request.method == 'POST':
#         form = MessageForm(request.POST)
#         if form.is_valid():
#             message = form.save(commit=False)
#             message.user = request.user
#             message.room = Room.objects.get(id=pk)
#             message.save()
#             return redirect('room', pk)
#     context = {'form': form}
#     return render(request, 'base/create_message.html', context)