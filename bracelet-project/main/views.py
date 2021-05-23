from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import Group, User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
from .models import Contact, Post
from django.core.files.storage import FileSystemStorage
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import datetime
from django.core.files import File


# Create your views here.

def is_contact_resent(contact):
	compare = contact.date.date() - datetime.date.today()
	return compare.days < 0 and compare.days > -15

def can_i_let_him_in(request):
	return (request.user.is_authenticated and not request.user.is_superuser)

def forbidden_page(request):
	return render(request, 'forbidden.html')

def home(request):
	if not can_i_let_him_in(request):
		return redirect('login')

	posts = Post.objects.all()
	if request.user.is_staff:
		render(request, 'home.html', {'posts' : posts[:5]})

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
	for contact in our_contact_list:
		if contact.first_user == our_user and not contacts_with.count(contact.second_user):
			contacts_with.append(contact.second_user)
		elif contact.second_user == our_user and not contacts_with.count(contact.first_user):
			contacts_with.append(contact.first_user)
	return render(request, 'home.html', {'posts' : posts[:5], 'ill' : request.user.groups.filter(name='ill').exists(),
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
	messege = None
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)  # Important!
			messege = "Ваш пароль был успешно изменен"
		else:
			messege = "Форма смены пароля невалидна"
	else:
		form = PasswordChangeForm(request.user)
	return render(request, 'change_password.html', {'form': form, 'messege' : messege})

def account(request):
	if not can_i_let_him_in(request):
		return redirect('login')

	return render(request, 'account.html', {'ill' : request.user.groups.filter(name='ill').exists()})

def contacts(request):
	if not can_i_let_him_in(request):
		return redirect('login')

	user = request.user
	contact_list = Contact.objects.all()
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

def info_about_person(request, user_id, messege=None):
	if not can_i_let_him_in(request):
		return redirect('login')
	if not request.user.is_staff:
		return forbidden_page(request)

	messege = None
	user = User.objects.get(id=user_id)
	if request.method == 'POST':
		res = change_the_health_status(request, user_id)
		if user.groups.filter(name='ill').exists():
			if res == 0:
				messege = "Пользователи, контактировавшие с данным сотрудником, оповещены"
			else:
				messege = "Произошла ошибка при оповещении сотрудников, попробуйте еще раз"
				user.groups.remove(Group.objects.get(name='ill'))
	

	contact_list =  Contact.objects.all()
	our_contact_list = []
	for contact in contact_list:
		if contact.first_user.username == user.username or contact.second_user.username == user.username:
			our_contact_list.append(contact)
	return render(request, 'about_person.html', {'user' : user, 'contacts' : our_contact_list,
		'empty' : len(our_contact_list) == 0, 'ill' : user.groups.filter(name='ill').exists(), 'messege' : messege})

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
		contact_list = Contact.objects.all()
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

def notify_user(users):
	addr_from = "anticovidbracelet@yandex.com"
	password  = "bisxbtrjucwaebfi"

	recipients = [user.email for user in users]
	msg = MIMEMultipart()
	msg['From']    = addr_from
	msg['To']      = ", ".join(recipients)
	msg['Subject'] = 'Информация от антиковидного браслета'

	text = "Здравствуйте.\nПо нашим данным, за последние две недели у вас был контакт с человеком, заболевшим коронавирусной инфекцией. Просим вас сдать пцр-тест на covid 19 и не приходить на работу до получения отрицательного результата."
	msg.attach(MIMEText(text, 'plain'))
	try:
		server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
		server.login(addr_from, password)
		server.sendmail(addr_from, recipients, msg.as_string())
		server.quit()
		return 0
	except:
		return 1

def change_the_health_status(request, user_id):
	if not can_i_let_him_in(request):
		return redirect('login')
	if not request.user.is_staff:
		return forbidden_page(request)

	# messege = None
	group = Group.objects.get(name='ill')
	user = User.objects.get(id=user_id)
	if user.groups.filter(name='ill').exists():
		user.groups.remove(group)
		return 0
	else:
		user.groups.add(group)
		contact_list =  Contact.objects.all()
		our_contact_list = []
		for contact in contact_list:
			if contact.first_user.username == user.username or contact.second_user.username == user.username:
				our_contact_list.append(contact)
		send_to = []
		for contact in our_contact_list:
			if is_contact_resent(contact) and contact.first_user == user and not contact.second_user.groups.filter(name='ill').exists() and not send_to.count(contact.second_user):
				# notify_user(contact.second_user)
				send_to.append(contact.second_user)
			elif is_contact_resent(contact) and contact.second_user == user and not contact.first_user.groups.filter(name='ill').exists() and not send_to.count(contact.first_user):
				# notify_user(contact.first_user)
				send_to.append(contact.first_user)
		return notify_user(send_to)
		# messege = "Пользователи, контактировавшие с данным сотрудником, оповещены"

	# return redirect('info_about_person', user_id)
	# redirect('info_about_person', user_id)
	# return info_about_person(request, user_id, messege)

def check_file(array):
	correct = []
	for i in range(len(array)):
		item = array[i]
		if not item.isspace() and item != '':
			includes = item.split(' ')
			if not User.objects.filter(username=includes[0]).exists():
				return "Неопознанный пользователь '" + includes[0] + "' в строке '" + item + "' [" + str(i + 1) + "]"
			if not User.objects.filter(username=includes[1]).exists():
				return "Неопознанный пользователь '" + includes[1] + "' в строке '" + item + "' [" + str(i + 1) + "]"
			if len(includes[2]) != 10:
				return "Неверный формат даты в строке '" + item + "' [" + str(i + 1) + "]"
			if not (includes[2][2] == '/' and includes[2][5] == '/' and includes[2][0:2].isdigit() and includes[2][3:5].isdigit() and includes[2][6:].isdigit()):
				return "Неверный формат даты в строке '" + item + "' [" + str(i + 1) + "]"

			d = int(includes[2][0:2])
			m = int(includes[2][3:5])
			y = int(includes[2][6:])
			try:
				our_date = datetime.date(y, m, d)
			except:
				return "Некорректная дата в строке '" + item + "' [" + str(i + 1) + "]"
			compare = our_date - datetime.date.today()
			if compare.days > 0:
				return "Дата в данной строке еще не наступила: '" + item + "' [" + str(i + 1) + "]"
			if compare.days < -60:
				return "В данной строке указана дата, которой больше 2 месяцев: '" + item + "' [" + str(i + 1) + "]"

			if len(includes[3]) != 5 and len(includes[3]) != 6:
				return "Неверный формат времени в строке '" + item + "' [" + str(i + 1) + "]"
			if not (includes[3][2] == ':' and includes[3][0:2].isdigit() and includes[3][3:5].isdigit()):
				return "Неверный формат времени в строке '" + item + "' [" + str(i + 1) + "]"

			h = int(includes[3][0:2])
			mi = int(includes[3][3:5])
			try:
				our_time = datetime.time(h, mi)
			except:
				return "Некорректное время в строке '" + item + "' [" + str(i + 1) + "]"
			if our_date == datetime.date.today():
				time_now = datetime.datetime.now().time()
				if (time_now.hour * 60 + time_now.minute) < (our_time.hour * 60 + our_time.minute):
					return "В данной строке указана сегодняшняя дата, но еще не наступившее время: '" + item + "' [" + str(i + 1) + "]"
			user1 = get_object_or_404(User, username=includes[0])
			user2 = get_object_or_404(User, username=includes[1])
			# c = Contact.objects.create(first_user=user1, second_user=user2, date=datetime.datetime(y, m, d, h, m))
			data = datetime.datetime(y, m, d, h, mi)

			correct.append([user1, user2, data])
	return correct

def create_new_contacts(array):
	contacts_array = []
	array.sort(key=lambda x: x[2])
	for i in range(len(array)):
		ok = True
		for j in contacts_array:
			if (j[0] == array[i][0] and j[1] == array[i][1]) or (j[0] == array[i][1] and j[1] == array[i][0]):
				if j[2].date() == array[i][2].date():
					compare = (j[2].hour * 60 + j[2].minute) - (array[i][2].hour * 60 + array[i][2].minute)
					if compare <= 30 and compare >= -30:
						ok = False
		if ok:
			contacts_array.append(array[i])
	old_contacts = Contact.objects.all()
	will_be_saved = []
	for i in contacts_array:
		ok = True
		for j in old_contacts:
			if (j.first_user == i[0] and j.second_user == i[1]) or (j.first_user == i[1] and j.second_user == i[0]):
				if j.date.date() == i[2].date():
					compare = (j.date.hour * 60 + j.date.minute) - (i[2].hour * 60 + i[2].minute)
					if compare <= 30 and compare >= -30:
						ok = False
		if ok:
			will_be_saved.append(i)
	print(len(will_be_saved))
	return will_be_saved


def take_contacts(request):
	if not can_i_let_him_in(request):
		return redirect('login')
	if not request.user.is_staff:
		return forbidden_page(request)

	if request.method == 'POST':
		if request.FILES.get('myfile') == None:
			return render(request, 'take_file.html', {
			'messege': "Необходимо загрузить файл"})
		if str(request.FILES.get('myfile'))[-4:] != '.txt':
			return render(request, 'take_file.html', {
			'messege': "Неверный формат файла '" + str(request.FILES.get('myfile')) + "'"})

		text = request.FILES["myfile"].read()
		text = text.decode("utf-8")
		text = text.split('\n')
		res = check_file(text)
		if type(res) == str:
			return render(request, 'take_file.html', {
			'messege': 'ОШИБКА: ' + res}) 
		res = create_new_contacts(res)
		if len(res) == 0:
			return render(request, 'take_file.html', {
		'messege': 'Все контакты из данного файла дублируются с контактами, уже имеющимися в базе данных. Новых контактов не добавлено'})

		for item in res:
			c = Contact.objects.create(first_user=item[0], second_user=item[1], date=item[2])
		text = "Успешно! Колличество добавленных контактов: " + str(len(res))

		return render(request, 'take_file.html', {
			'messege': text})
	return render(request, 'take_file.html')


def delete_old_contacts(request):
	if not can_i_let_him_in(request):
		return redirect('login')
	if not request.user.is_staff:
		return forbidden_page(request)

	messege = None
	if request.method == 'POST':
		start = None
		contacts_list = Contact.objects.all()
		for i in range(len(contacts_list)):
			if not is_contact_resent(contacts_list[i]):
				start = i
				break
		if start != None:
			count = 0
			for i in range(start, len(contacts_list)):
				contacts_list[i].delete()
				count += 1
		if start != None and count != 0:
			messege = "Успешно! Колличество удаленных контактов: " + str(count)
		else:
			messege = "Подходящих контактов не найдено. Ни один контакт не был удален."

	return render(request, 'delete_old_contacts.html', {
			'messege': messege})

from django.http import HttpResponse, FileResponse
from django.core.files.base import ContentFile


def contacts_download(request):
	if not can_i_let_him_in(request):
		return redirect('login')
	if not request.user.is_staff:
		return forbidden_page(request)

	contacts_list = Contact.objects.all()
	str_for_user = ''
	for contact in contacts_list:
		str_for_user += contact.first_user.username + ' ' + contact.second_user.username + ' '
		if contact.date.date().day < 10:
			str_for_user += '0'
		str_for_user += str(contact.date.date().day) + '/'
		if contact.date.date().month < 10:
			str_for_user += '0'
		str_for_user += str(contact.date.date().month) + '/' + str(contact.date.date().year) + ' '
		if contact.date.time().hour < 10:
			str_for_user += '0'
		str_for_user += str(contact.date.time().hour) + ':'
		if contact.date.time().minute < 10:
			str_for_user += '0'
		str_for_user += str(contact.date.time().minute) + '\n'


	file_to_send = ContentFile(str_for_user)
	response = HttpResponse(file_to_send,'application/x-gzip')
	response['Content-Length'] = file_to_send.size    
	response['Content-Disposition'] = 'attachment; filename="Contacts.txt"'
	return response 