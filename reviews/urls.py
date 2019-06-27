from django.conf.urls import url
from django.urls import path, include
from . import views

urlpatterns = [

    # path('', views.ReviewListView, name='review_changelist'),
    # path('add/', views.ReviewCreateView, name='review_add'),
    # path('<int:pk>/', views.ReviewUpdateView.as_view(), name='review_change'),
    #path('ajax/load-restaurants/', views.load_restaurants, name='ajax_load_restaurants'), # <-- this one here
    
    # ex: /
    url(r'^$', views.review_list, name='review_list'),
    url(r'^denied/$', views.denied, name='denied'),
    url(r'^invite/(?P<department_id>[0-9]+)/$', views.invite, name='invite'),
    # ex: /review/5/
    url(r'^review/(?P<review_id>[0-9]+)/$', views.review_detail, name='review_detail'),
    # ex: /wine/
    url(r'^departments$', views.department_list_all, name='department_list_all'),
    url(r'^(?P<college_id>[0-9]+)/departments/$', views.department_list, name='department_list'),
    url(r'^class$', views.restaurant_list, name='restaurant_list'),
    # ex: /wine/5/

    url(r'^department/(?P<department_id>[0-9]+)/$', views.department_detail, name='department_detail'),
    url(r'^topic/(?P<topic_id>[0-9]+)/$', views.topic_detail, name='topic_detail'),
    url(r'^class/(?P<restaurant_id>[0-9]+)/$', views.restaurant_detail, name='restaurant_detail'),
    url(r'^class/(?P<restaurant_id>[0-9]+)/add_review/$', views.add_review, name='add_review'),
    url(r'^department/(?P<department_id>[0-9]+)/add_topic/$', views.add_topic, name='add_topic'),
    url(r'^topic/(?P<topic_id>[0-9]+)/add_response/$', views.add_response, name='add_response'),
    url(r'^user/(?P<username>\w+)/profile/$', views.user_profile, name='user_profile'),
    url(r'^user/(?P<username>\w+)/add_profile/$', views.add_profile, name='add_profile'),
    url(r'^review/(?P<department_id>[0-9]+)/sub/$', views.sub_dept, name='sub_dept'),
    url(r'^review/(?P<department_id>[0-9]+)/unsub/$', views.unsub_dept, name='unsub_dept'),

    # Report, edit, delete, like URLS
    url(r'^class/find_review/$', views.find_review, name='find_review'),
    url(r'^class/find_review/(?P<department_id>[0-9]+)/$', views.find_review_result, name='find_review_result'),
    url(r'^class/add_general_review/$', views.add_general_review, name='add_general_review'),
    url(r'^review/(?P<review_id>[0-9]+)/edit/$', views.edit_review, name='edit_review'),
    url(r'^review/(?P<review_id>[0-9]+)/delete/$', views.delete_review, name='delete_review'),
    url(r'^review/(?P<review_id>[0-9]+)/report/$', views.report_review, name='report_review'),
    url(r'^review/(?P<review_id>[0-9]+)/like/$', views.like_review, name='like_review'),

    url(r'^topic/(?P<topic_id>[0-9]+)/edit/$', views.edit_topic, name='edit_topic'),
    url(r'^topic/(?P<topic_id>[0-9]+)/delete/$', views.delete_topic, name='delete_topic'),
    url(r'^topic/(?P<topic_id>[0-9]+)/report/$', views.report_topic, name='report_topic'),
    url(r'^topic/(?P<topic_id>[0-9]+)/like/$', views.like_topic, name='like_topic'),

    #url(r'^user/(?P<username>\w+)/$', views.user_review_list, name='user_review_list'),
    url(r'^user/$', views.user_profile, name='user_profile'),
    url(r'^recommendation/$', views.user_recommendation_list, name='user_recommendation_list'),
    ]