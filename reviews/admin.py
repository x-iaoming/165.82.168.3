from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Restaurant, Review, Cluster, College, Department, Topic, Response, Profile

class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    list_display = ['user','college','year']
    list_filter = ['college','year']

class ReviewAdmin(admin.ModelAdmin):
    model = Review
    list_display = ('restaurant','rating','user_name','prof_name','comment',
        'pub_date','pre_req','materials','class_size',
        'assessment','work_load','diff_level','get_report_counts','get_like_counts')
    list_filter = ['pub_date','user_name','class_size','assessment','work_load','prof_name','diff_level']
    search_fields = ['comment']

class ReviewRestaurant(admin.ModelAdmin):
    model = Restaurant
    list_display = ('name','department')
    list_filter = ['department']
    search_fields = ['name']

class DepartmentAdmin(admin.ModelAdmin):
    model = Department
    list_display = ('name','college','get_subs')

class TopicAdmin(admin.ModelAdmin):
    model = Topic
    list_display = ('user_name','title','content','pub_date')
    search_fields = ['department']

class ClusterAdmin(admin.ModelAdmin):
    model = Cluster
    list_display = ['name', 'get_members']

class CollegeAdmin(admin.ModelAdmin):
    model = College
    list_display = ['name']

class ResponseAdmin(admin.ModelAdmin):
    model = Response
    list_display = ['content','user_name','pub_date']
# class UserProfileInline(admin.StackedInline):
#     model = UserProfile
#     can_delete = True
#     verbose_name_plural = 'userprofile'

# class UserAdmin(BaseUserAdmin):
#     inlines = (UserProfileInline,)

#admin.site.unregister(User)
#admin.site.register(User, UserAdmin)
admin.site.register(Restaurant,ReviewRestaurant)
admin.site.register(Review,ReviewAdmin)
admin.site.register(Cluster,ClusterAdmin)
admin.site.register(College,CollegeAdmin)
admin.site.register(Department,DepartmentAdmin)
admin.site.register(Topic,TopicAdmin)
admin.site.register(Response,ResponseAdmin)
admin.site.register(Profile,ProfileAdmin)

