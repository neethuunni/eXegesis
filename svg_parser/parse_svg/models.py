from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Project(models.Model):
	email = models.CharField(max_length=50)
	project = models.CharField(max_length=50)
	description = models.CharField(max_length=100)
	share = models.BooleanField(default=False)
	edit = models.BooleanField(default=False)

	def __str__(self):
		return str(self.email) + '  ' + str(self.project) +  '  ' + str(self.description)

class ArtBoard(models.Model):
	project = models.ForeignKey(Project)
	artboard = models.CharField(max_length=50)
	location = models.CharField(max_length=100)

	def __str__(self):
		return str(self.project) + '  ' + str(self.artboard) +  '  ' + str(self.location)
