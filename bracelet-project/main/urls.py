from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='home'),
	path('account/login/', views.loginView, name='login'),
	path('account/signout/', views.signoutView, name='signout'),
	path('account', views.account, name='account'),
	path('contacts', views.contacts, name='contacts'),
	path('contacts/account/<int:user_id>', views.info_about_person, name='info_about_person'),
	path('illnes', views.illnes, name='illnes'),
	path('account/change_password', views.change_password, name='change_password'),
	path('account/change_password/successfully', views.successfull_password_change, name='successfull_password_change'),
]