from __future__ import unicode_literals

from django.db import models

# https://docs.djangoproject.com/en/1.9/ref/models/fields/#django.db.models.ForeignKey
# http://stackoverflow.com/questions/12610337/many-to-many-relation-orm-django
# https://docs.djangoproject.com/en/1.9/topics/db/examples/many_to_many/
class Category(models.Model):
	tag = models.CharField(max_length=200)

	def __str__(self):
		return self.tag


class Items(models.Model):
	title = models.CharField(max_length=200)
	description = models.CharField(max_length=600)
	price = models.IntegerField(default=15)
	tags = models.ManyToManyField(Category)
	#image = models.ImageField(required=False)

	def __str__(self):
		return self.title

#class ItemCategory(models.Model):
#	item = models.ForeignKey(Items, on_delete=models.CASCADE)
#	itemcat = models.ForeignKey(Category, on_delete=models.CASCADE)