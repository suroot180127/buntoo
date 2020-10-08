# Imports from built-in Django stuff
from django.shortcuts import render, redirect
from django.contrib import messages  # import flash messages
# import stops user from accessing routes if their not logged in
from django.contrib.auth.decorators import login_required
from . import views
from trading.models import Friend_List
# Imports from apps you've made
# the form you created in forms.py that inherits from Django's UserCreationForm
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import *
from trading.models import *
from trading.forms import PostForm
from itertools import chain
import json
from django.contrib import auth
from django.http import HttpResponseRedirect
# Create your views here.


# User Registration form using Djangos built-in User Form
# Register new User
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()  # Save users data to database create and save new user from form data
            username = form.cleaned_data.get('username')  # get the username
            password = form.cleaned_data.get('password1')  # get the username
            user = auth.authenticate(username=username, password=password)
            # return HttpResponseRedirect("home_page")

            # show a flash message
            # messages.success(request, f'Account created successfully! Now you can login.')
            # return render(request, 'login')
            if user is not None:
            # correct username and password login the user
                auth.login(request, user)
                return redirect('home_page')
            else:
                print('''
                -----------------------------
                -----------------------------
                -----------------------------''')
        else:
            messages.warning(request, 'Check email. Password should be 8 or more mixed characters.')
            return render(request, 'trading/landing-page.html')

    if request.method == 'GET':
        form = UserRegisterForm()    
        # messages.warning(request, 'Form Validation Failed. Try Again.')
        return render(request, 'trading/landing-page.html')

    return render(request, 'trading/landing-page.html', {'form': form})


def login(request):
    if request.user.is_authenticated:
        return redirect('home_page')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            # correct username and password login the user
            auth.login(request, user)
            return redirect('home_page')

        else:
            messages.warning(request, 'Error: Wrong username or password')

    return render(request, 'trading/landing-page.html')

def logout(request):
    auth.logout(request)
    messages.success(request, "Logged Out Successfully!")
    return render(request,'trading/landing-page.html')


# a built-in decorator that requires the user to be logged in to access this view
@login_required
def user_profile(request):
    ######################################
    user_list = []
    for i in User.objects.all():
        user_list.append(i.username)
    user_list_json=json.dumps(user_list)
    userzero = User.objects.all()[0]
    ######################################
    form = PostForm()
    
    if request.method == 'POST' \
        and request.POST.get("form_name", None) == "post_form":
        
        form = PostForm(request.POST, request.FILES)
        
        if form.is_valid():
            new = form.save(commit=False)
            new.author = request.user
            form.save()
            new.save()
            return redirect('landing_page')

    ######################################
    if request.method == 'POST' and request.POST.get("form_name", None) == "user_info":
        user_update_form = UserUpdateForm(request.POST, instance=request.user)
        profile_update_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile)

        if user_update_form.is_valid() and profile_update_form.is_valid():
            user_update_form.save()
            
            # set commit = false to get the user object
            # then you need to set the user object to Profile Instance
            # and finally save
            _tmpProfile = profile_update_form.save(commit=False)
            _tmpProfile.user = request.user
            _tmpProfile.save()

            messages.success(request, f'Your account has been updated!')
            return redirect('user_profile')
    else:
        user_update_form = UserUpdateForm(instance=request.user)
        profile_update_form = ProfileUpdateForm(instance=request.user.profile)
    
    try:
        friend = Friend_List.objects.get(user=request.user).friend_name.all()
    except:
        friend=None

    posts = Post.objects.filter(author=request.user)
    # for i in current_user:
    #     current.append(i)
    # posts = []
    # user_profile = Profile.objects.get(user=request.user)
    # try:
    #     friends = user_profile.friends.friend_name.all() 
    #     for i in friends:
    #         posts.append(Post.objects.filter(author=i).order_by('-date_posted'))
    #     posts_sorted=[]
    #     for i in posts:
    #         for j in i:    
    #             posts_sorted.append(j) 
    # except:
    #     posts=[]
    #     posts_sorted=[]
 

    # for i in current_user:
    #     posts_sorted.append(i)

    # posts = sorted(list(chain(posts_sorted)),key= lambda instance:instance.date_posted)[::-1]
    # all_ads = advert.objects.all()
    # alist = {}

    # count = 0

    # for i in posts:
    #     if count == 8:
    #         try:
    #             alist['a'+str(len(alist))] = all_ads[random.randint(0,len(all_ads)-1)]
    #         except:
    #             alist['p'+str(len(alist))] = i
    #         count = 0
    #     else:
    #         alist['p'+str(len(alist))] = i
    #         count = count + 1
    
    # blist = []
    # clist = []
    # for i,j in alist.items():
    #     clist.append(j)
    #     if i[0] == 'a':
    #         blist.append(True)
    #     else:
    #         blist.append(False)
    # empty = -1
    # if not blist and not clist:
    #     empty = 1 



    objs = advert.objects.filter(author=request.user)
    context = {
        'ads':objs,
        'user_update_form': user_update_form,
        'profile_update_form': profile_update_form,
        'friend_List':friend,
        'userzero':userzero,
        'posts': posts,
    }
    # render html from templates folder and pass in data using context
    return render(request, 'users/user_profile.html', context)


def profile(request,user):
     ######################################
    user_list = []
    friends_list = []
    for i in User.objects.all():
        user_list.append(i.username)
    user_list_json=json.dumps(user_list)
    userzero = User.objects.all()[0]


    ######################################
    user_profile = Profile.objects.get(user=user)
    print(user_profile)
    try:
        friends = Friend_List.objects.filter(user=user).values('friend_name')
        for i in friends:
            user = User.objects.get(id=i['friend_name'])
            friends_list.append(user)
        posts =  Post.objects.filter(author=user_profile.user)
        print(posts)
    except:
        friend=None
    context = {
        'user_profle': user_profile,
        'user_list_json':user_list_json,
        'userzero':userzero,
        'friends':friends_list,
        'posts':posts
       
    }
    return render(request, 'users/profile.html', context)
