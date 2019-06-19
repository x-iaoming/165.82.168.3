from django.contrib import admin
from .models import Restaurant, Review, Cluster

class ReviewAdmin(admin.ModelAdmin):
	model = Review
	list_display = ('restaurant','rating','user_name','prof_name','comment','pub_date','pre_req','materials','class_size','assessment','work_load','diff_level')
	list_filter = ['pub_date','user_name','class_size','assessment','work_load','prof_name','diff_level']
	search_fields = ['comment']

class ReviewRestaurant(admin.ModelAdmin):
	model = Restaurant
	list_display = ('name','school')
	list_filter = ['school']
	search_fields = ['name']

class ClusterAdmin(admin.ModelAdmin):
    model = Cluster
    list_display = ['name', 'get_members']

admin.site.register(Restaurant,ReviewRestaurant)
admin.site.register(Review,ReviewAdmin)
admin.site.register(Cluster,ClusterAdmin)
