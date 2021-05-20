from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import Group, User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
from .models import Contact, Post
from django.core.files.storage import FileSystemStorage


# Create your views here.

def can_i_let_him_in(request):
	return (request.user.is_authenticated and not request.user.is_superuser)

def forbidden_page(request):
	return render(request, 'forbidden.html')

def home(request):
	if not can_i_let_him_in(request):
		return redirect('login')

	posts = Post.objects.all()
	if request.user.is_staff:
		render(request, 'home.html', {'posts' : posts})

	our_user = request.user
	contact_list =  Contact.objects.all()
	our_contact_list = []
	for contact in contact_list:
		if contact.first_user.username == our_user.username or contact.second_user.username == our_user.username:
			our_contact_list.append(contact)
	users = User.objects.all()
	all = 0
	ill_users = []
	for user in users:
		if user.groups.filter(name='ill').exists():
			ill_users.append(user)
		if not user.is_staff and not user.is_superuser:
			all += 1

	probably_ill = False
	for contact in our_contact_list:
		if contact.first_user != our_user and ill_users.count(contact.first_user):
			probably_ill = True
			break
		elif contact.second_user != our_user and ill_users.count(contact.second_user):
			probably_ill = True
			break
	contacts_with = []
	for contact in our_contact_list[0:3]:
		if contact.first_user == our_user:
			contacts_with.append(contact.second_user)
		else:
			contacts_with.append(contact.first_user)
	return render(request, 'home.html', {'posts' : posts, 'ill' : request.user.groups.filter(name='ill').exists(),
					'probably_ill' : probably_ill, 'contacts_with' : contacts_with, 'all' : all, 'ill_size' : len(ill_users)})
	

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

def change_password(request):
	if not can_i_let_him_in(request):
		return redirect('login')

	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)  # Important!
			messages.success(request, 'Your password was successfully updated!')
			return redirect('successfull_password_change')
		else:
			messages.error(request, 'Please correct the error below.')
	else:
		form = PasswordChangeForm(request.user)
	return render(request, 'change_password.html', {'form': form})

def successfull_password_change(request):
	if not can_i_let_him_in(request):
		return redirect('login')

	return render(request, 'successfull_password_change.html')

def account(request):
	if not can_i_let_him_in(request):
		return redirect('login')

	return render(request, 'account.html', {'ill' : request.user.groups.filter(name='ill').exists()})

def contacts(request):
	if not can_i_let_him_in(request):
		return redirect('login')

	user = request.user
	contact_list =  Contact.objects.all()
	if user.is_staff:
		return render(request, 'contacts.html', {'contacts' : contact_list, 'empty' : len(contact_list) == 0, 'to_ill' : True})
	our_contact_list = []
	for contact in contact_list:
		if contact.first_user.username == user.username or contact.second_user.username == user.username:
			our_contact_list.append(contact)
	return render(request, 'contacts.html', {'contacts' : our_contact_list, 'empty' : len(our_contact_list) == 0})

def only_ill_contacts(request):
	if not can_i_let_him_in(request):
		return redirect('login')
	if not request.user.is_staff:
		return forbidden_page(request)

	user = request.user
	contact_list =  Contact.objects.all()
	only_ill_contacts = []
	for contact in contact_list:
		if contact.first_user.groups.filter(name='ill').exists() or contact.second_user.groups.filter(name='ill').exists():
			only_ill_contacts.append(contact)
	return render(request, 'contacts.html', {'contacts' : only_ill_contacts, 'empty' : len(only_ill_contacts) == 0, 'to_ill' : False})

def info_about_person(request, user_id):
	if not can_i_let_him_in(request):
		return redirect('login')
	if not request.user.is_staff:
		return forbidden_page(request)

	user = User.objects.get(id=user_id)

	contact_list =  Contact.objects.all()
	our_contact_list = []
	for contact in contact_list:
		if contact.first_user.username == user.username or contact.second_user.username == user.username:
			our_contact_list.append(contact)
	return render(request, 'about_person.html', {'user' : user, 'contacts' : our_contact_list,
		'empty' : len(our_contact_list) == 0, 'ill' : user.groups.filter(name='ill').exists()})

def illnes(request):
	if not can_i_let_him_in(request):
		return redirect('login')
	if not request.user.is_staff:
		return forbidden_page(request)

	users = User.objects.all()
	ill_users = []
	for user in users:
		if user.groups.filter(name='ill').exists():
			ill_users.append(user)
	passibly_ill = []
	if len(ill_users) != 0:
		contact_list =  Contact.objects.all()
		for contact in contact_list:
			if ill_users.count(contact.first_user):
				if ill_users.count(contact.second_user) == 0 and passibly_ill.count(contact.second_user) == 0:
					passibly_ill.append(contact.second_user)

			if ill_users.count(contact.second_user):
				if ill_users.count(contact.first_user) == 0 and passibly_ill.count(contact.first_user) == 0:
					passibly_ill.append(contact.first_user)


	return render(request, 'illnes.html', {'ill_users' : ill_users, 'empty_ill' : len(ill_users) == 0,
											'passibly_ill' : passibly_ill, 'empty_passibly_ill' : len(passibly_ill) == 0})


def workersView(request):
	if not can_i_let_him_in(request):
		return redirect('login')
	if not request.user.is_staff:
		return forbidden_page(request)

	users = User.objects.all()
	workers = []
	for user in users:
		if not user.is_staff and not user.is_superuser:
			workers.append(user)
	
	return render(request, 'workers.html', {'workers' : workers, 'empty' : len(workers) == 0})

def change_the_health_status(request, user_id):
	if not can_i_let_him_in(request):
		return redirect('login')
	if not request.user.is_staff:
		return forbidden_page(request)

	group = Group.objects.get(name='ill')
	user = User.objects.get(id=user_id)
	if user.groups.filter(name='ill').exists():
		user.groups.remove(group)
	else:
		user.groups.add(group)

	return redirect('info_about_person', user_id)

def take_contacts(request):
	if request.method == 'POST' and request.FILES['myfile']:
		myfile = request.FILES['myfile']
		fs = FileSystemStorage()
		filename = fs.save(myfile.name, myfile)
		uploaded_file_url = fs.url(filename)
		return render(request, 'take_file.html', {
			'uploaded_file_url': uploaded_file_url
		})
	return render(request, 'take_file.html')