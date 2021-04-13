from django.db import models
from django.contrib.auth.models import Group, User

# Create your models here.
class Contact(models.Model):
	first_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
	second_user = models.ForeignKey(User, on_delete=models.CASCADE,  related_name='+')
	date = models.DateTimeField()
	# name = models.CharField(max_length=250, unique=True, default='name')

	class Meta:
		ordering = ('date', )
		verbose_name = 'контакт'
		verbose_name_plural = 'контакты'

	def __str__(self):
		return self.first_user.last_name + ' - ' + self.second_user.last_name + ', ' + str(self.date)