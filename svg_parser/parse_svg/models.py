from __future__ import unicode_literals

from django.db import models

from django.utils import timezone


# Create your models here.

class Project(models.Model):
	email = models.CharField(max_length=50)
	project = models.CharField(max_length=50)
	description = models.CharField(max_length=100)
	share = models.BooleanField(default=False)
	edit = models.BooleanField(default=False)
	thumbnail = models.CharField(max_length=100)
	owner = models.CharField(max_length=50)
	screen = models.CharField(max_length=10, default='')
	density = models.CharField(max_length=10, blank=True, null=True)
	created = models.DateTimeField(default=timezone.now)
	last_updated = models.DateTimeField(default=timezone.now)
	uuid = models.CharField(max_length=50, default='')

	def __str__(self):
		return str(self.email) + ', ' + str(self.project) +  ', '

class ArtBoard(models.Model):
	project = models.ForeignKey(Project)
	artboard = models.CharField(max_length=50)
	location = models.CharField(max_length=100)
	uuid = models.CharField(max_length=50, default='')

	def __str__(self):
		return str(self.project) + ', ' + str(self.artboard) +  ', ' + str(self.location)
