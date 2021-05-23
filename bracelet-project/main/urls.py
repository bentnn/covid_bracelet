from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='home'),
	path('account/login/', views.loginView, name='login'),
	path('account/signout/', views.signoutView, name='signout'),
	path('account', views.account, name='account'),
	path('contacts', views.contacts, name='contacts'),
	path('contacts/ill', views.only_ill_contacts, name='only_ill_contacts'),
	path('workers/<int:user_id>', views.info_about_person, name='info_about_person'),
	path('illnes', views.illnes, name='illnes'),
	path('account/change_password', views.change_password, name='change_password'),
	path('workers', views.workersView, name='workers'),
	path('take_contacts', views.take_contacts, name='take_contacts'),
]