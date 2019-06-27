from django.db import models
import numpy as np
from django.contrib.auth.models import User

class College(models.Model):
    name = models.CharField(max_length=30,null=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    college = models.ForeignKey(College,on_delete=models.CASCADE, null=True)
    year = models.IntegerField(null=True)

class Department(models.Model):
    name = models.CharField(max_length=30,null=True)
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True)
    sub = models.ManyToManyField(User,blank=True)

    def __str__(self):
        return self.name

    def get_subs(self):
        return "\n".join([u.username for u in self.sub.all()])

    def sub_count(self):
        return self.sub.all().count()

class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    done = models.ManyToManyField(User,related_name='done',blank=True)

    def average_rating(self):
        all_ratings = map(lambda x: x.rating, self.review_set.all())
        return np.mean(list(all_ratings))

    def average_diff(self):
        all_diff = map(lambda x: x.diff_level, self.review_set.all())
        return np.mean(list(all_diff))

    def average_wl(self):
        all_wl = map(lambda x: x.work_load, self.review_set.all())
        return np.mean(list(all_wl))

    def __str__(self):
        return self.name

class Review(models.Model):
    RATING_CHOICES = (
        (1,'1'),
        (2,'2'),
        (3,'3'),
        (4,'4'),
        (5,'5'),
    )

    # ASSESSMENTS = (
    #     (1,'Problem sets'),
    #     (2,'Projects'),
    #     (3,'Presentations'),
    #     (4,'Exams'),
    #     (5,'Papers')
    # )

    CLASS_SIZE = (
        (1,'Small:1-10'),
        (2,'Medium:10-20'),
        (3,'Large:20+'),
    )

    WORK_LOAD = (
    	(1,'Light:<=3 hours/week'),
    	(2,'Medium:<=6 hours/week'),
    	(3,'Heavy:<=10 hours/week'),
    	(4,'Insane:>10 hours/week'),
    )

    DIFF_LEVEL = (
    	(1,'VeryEasy'),
        (2,'Easy'),
    	(3,'Manageable'),
    	(4,'Challenging'),
    	(5,'Suffocating'),
    )

    ANONY = (
        (False,'False'),
        (True,'True:Your username is NOT recorded.You CANNOT modify this review later!!'),
    )

    restaurant = models.ForeignKey(Restaurant,on_delete=models.SET_NULL, null=True)
    college = models.ForeignKey(College,on_delete=models.SET_NULL, null=True)

    users_reported = models.ManyToManyField(User,blank=True)
    users_liked = models.ManyToManyField(User,related_name='users_liked_review',blank=True)
    
    pub_date = models.DateTimeField('date published',auto_now_add=True)
    user_name = models.CharField(max_length=100)
    prof_name = models.CharField(max_length=100,default='')
    comment = models.CharField(max_length=200)
    pre_req = models.CharField(max_length=100,default='')
    materials = models.CharField(max_length=100,default='')
    anonymous = models.BooleanField(choices=ANONY,default=False)

    rating = models.IntegerField(choices=RATING_CHOICES,default=5)
    assessment = models.CharField(max_length=400,null=True)
    class_size = models.IntegerField(choices=CLASS_SIZE,default=2)
    work_load = models.IntegerField(choices=WORK_LOAD,default=2)
    diff_level = models.IntegerField(choices=DIFF_LEVEL,default=2)

    def get_users_reported(self):
        return "\n".join([u.username for u in self.users_reported.all()])
    
    def get_report_counts(self):
        return self.users_reported.all().count()

    def get_users_liked(self):
        return "\n".join([u.username for u in self.users_liked.all()])

    def get_like_counts(self):
        return self.users_liked.all().count()

    def is_review(self):
        return True

    def set_anonoymous(self):
        if self.anonymous:
            self.user_name = 'anonymous_users'
    # def get_reports(self):
    #     return "\n".join([r.report_review for r in self.Review.all()])

    # def get_username(self):
    #     return "\n".join([u.username for u in self.users.all()])
class Topic(models.Model):
    ANONY = (
        (False,'False'),
        (True,'True:Your username is NOT recorded.You CANNOT modify this review later!!'),
    )

    user_name = models.CharField(max_length=100)
    title = models.CharField(max_length=30)
    content = models.CharField(max_length=200)
    department = models.ForeignKey(Department,on_delete=models.SET_NULL, null=True)
    anonymous = models.BooleanField(choices=ANONY,default=False)
    pub_date = models.DateTimeField('date published',null=True)
    users_reported = models.ManyToManyField(User,blank=True)
    users_liked = models.ManyToManyField(User,related_name='users_liked_topic',blank=True)

    def is_review(self):
        return False

    def get_like_counts(self):
        return self.users_liked.all().count()

class Response(models.Model):
    ANONY = (
        (False,'False'),
        (True,'True:Your username is NOT recorded.You CANNOT modify this review later!!'),
    )
    
    user_name = models.CharField(max_length=100)
    topic = models.ForeignKey(Topic,on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=200)
    anonymous = models.BooleanField(choices=ANONY,default=False)
    pub_date = models.DateTimeField('date published',null=True)
    users_reported = models.ManyToManyField(User,blank=True)
    users_liked = models.ManyToManyField(User,related_name='users_liked_response',blank=True)
    
    def get_like_counts(self):
        return self.users_liked.all().count()

class Cluster(models.Model):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User)

    def get_members(self):
        return "\n".join([u.username for u in self.users.all()])


