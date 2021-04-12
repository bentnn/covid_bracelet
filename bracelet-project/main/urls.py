from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='home'),
	path('help/', views.help, name='help'),
	path('account/login/', views.loginView, name='login'),
	path('account/signout/', views.signoutView, name='signout'),
	path('account', views.account, name='account'),
]