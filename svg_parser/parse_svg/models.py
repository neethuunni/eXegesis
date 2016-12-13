from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Image(models.Model):
	email = models.CharField(max_length=50)
	image = models.CharField(max_length=50)
	url = models.CharField(max_length=100)

	def __str__(self):
		return str(self.email) + '  ' + str(self.image) +  ' ' + str(self.url)