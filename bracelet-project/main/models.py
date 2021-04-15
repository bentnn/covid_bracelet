from django.db import models
from django.contrib.auth.models import Group, User

# Create your models here.
class Contact(models.Model):
	first_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
	second_user = models.ForeignKey(User, on_delete=models.CASCADE,  related_name='+')
	date = models.DateTimeField()
	# name = models.CharField(max_length=250, unique=True, default='name')

	class Meta:
		ordering = ('-date', )
		verbose_name = 'контакт'
		verbose_name_plural = 'контакты'

	def __str__(self):
		return self.first_user.last_name + ' - ' + self.second_user.last_name + ', ' + str(self.date)


class Post(models.Model):
	title = models.CharField(max_length=100)
	image = models.ImageField(upload_to='Post', blank=True)
	date = models.DateTimeField(auto_now_add=True)
	text = models.TextField(max_length=350, blank=True)

	class Meta:
		ordering = ('-date', )
		verbose_name = 'пост'
		verbose_name_plural = 'посты'

	def __str__(self):
		return self.title