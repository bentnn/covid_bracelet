from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import Group, User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
# Create your views here.
def home(request):
	if not request.user.is_authenticated:
		return redirect('login')
	return render(request, 'home.html')
	
def help(request):
	if not request.user.is_authenticated:
		return redirect('login')
	return render(request, 'help.html')

def loginView(request):
	if (request.method) == 'POST':
		form = AuthenticationForm(data=request.POST)
		if form.is_valid():
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				return redirect('home')
	else:
		form = AuthenticationForm()
	return render(request, 'login.html', {'form' : form})

def signoutView(request):
	logout(request)
	return redirect('login')