from .models import Restaurant, Review, Cluster, College, Department, Topic, Response, Profile
from django.shortcuts import get_object_or_404
import csv

path = '/Users/ruiming/Desktop/courses.csv'
with open(path) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            _, created = Department.objects.get_or_create(
                name=row[0],
                college=get_object_or_404(College,pk=1)
                )