from django.db import models
import numpy as np
from django.contrib.auth.models import User

class Restaurant(models.Model):
    SCHOOLS = (
    	('HC','Haverford'),
    	('BMC','Bryn Mawr'),
    	('SW','Swarthmore'),
    )

    name = models.CharField(max_length=200)
    school = models.CharField(max_length=3,choices=SCHOOLS,default='HC')

    def average_rating(self):
        all_ratings = map(lambda x: x.rating, self.review_set.all())
        return np.mean(list(all_ratings))

    def __unicode__(self):
        return self.name

class Review(models.Model):
    RATING_CHOICES = (
        (1,'1'),
        (2,'2'),
        (3,'3'),
        (4,'4'),
        (5,'5'),
    )

    ASSESSMENTS = (
        ('PS','Problem sets'),
        ('PJ','Projects'),
        ('PR','Presentations'),
        ('EX','Exams'),
        ('PP','Papers')
    )

    CLASS_SIZE = (
        ('S','Small:1-10'),
        ('M','Medium:10-20'),
        ('L','Large:20+'),
    )

    WORK_LOAD = (
    	('L','Light:<=3 hours/week'),
    	('M','Medium:<=6 hours/week'),
    	('H','Heavy:<=10 hours/week'),
    	('I','Insane:>10 hours/week'),
    )

    DIFF_LEVEL = (
    	('E','Easy'),
    	('M','Medium'),
    	('H','Hard'),
    	('I','Insane'),
    )

    restaurant = models.ForeignKey(Restaurant,on_delete=models.PROTECT)
    pub_date = models.DateTimeField('date published')
    user_name = models.CharField(max_length=100)
    prof_name = models.CharField(max_length=100,default='')
    comment = models.CharField(max_length=200)
    pre_req = models.CharField(max_length=100,default='')
    materials = models.CharField(max_length=100,default='')

    rating = models.IntegerField(choices=RATING_CHOICES)
    assessment = models.CharField(choices=ASSESSMENTS,max_length=2,default='EX')
    class_size = models.CharField(choices=CLASS_SIZE,max_length=1,default='M')
    work_load = models.CharField(choices=WORK_LOAD,max_length=2,default='M')
    diff_level = models.CharField(choices=DIFF_LEVEL,max_length=1,default='M')


class Cluster(models.Model):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User)
    def get_members(self):
        return "\n".join([u.username for u in self.users.all()])

