from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import Group, User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from .models import Contact

# Create your views here.

def can_i_let_him_in(request):
	return (request.user.is_authenticated and not request.user.is_superuser)

def home(request):
	if not can_i_let_him_in(request):
		return redirect('login')
	return render(request, 'home.html')
	
def help(request):
	if not can_i_let_him_in(request):
		return redirect('login')
	return render(request, 'help.html')

def loginView(request):
	if (request.method) == 'POST':
		form = AuthenticationForm(data=request.POST)
		if form.is_valid():
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(username=username, password=password)
			if user is not None and not user.is_superuser:
				login(request, user)
				return redirect('home')
	else:
		form = AuthenticationForm()
	return render(request, 'login.html', {'form' : form})

def signoutView(request):
	logout(request)
	return redirect('login')

def account(request):
	if not can_i_let_him_in(request):
		return redirect('login')
	return render(request, 'account.html')

def contacts(request):
	if not can_i_let_him_in(request):
		return redirect('login')
	user = request.user
	contact_list =  Contact.objects.all()
	if user.is_staff:
		return render(request, 'contacts.html', {'contacts' : contact_list, 'empty' : len(contact_list) == 0})
	our_contact_list = []
	for contact in contact_list:
		if contact.first_user.username == user.username or contact.second_user.username == user.username:
			our_contact_list.append(contact)
	return render(request, 'contacts.html', {'contacts' : our_contact_list, 'empty' : len(our_contact_list) == 0})
