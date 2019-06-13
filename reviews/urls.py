from django.conf.urls import url
#from django.urls import path
from . import views

urlpatterns = [
    # ex: /
    url(r'^$', views.review_list, name='review_list'),
    # ex: /review/5/
    url(r'^review/(?P<review_id>[0-9]+)/$', views.review_detail, name='review_detail'),
    # ex: /wine/
    url(r'^restaurant$', views.restaurant_list, name='restaurant_list'),
    # ex: /wine/5/
    url(r'^restaurant/(?P<restaurant_id>[0-9]+)/$', views.restaurant_detail, name='restaurant_detail'),
    url(r'^restaurant/(?P<restaurant_id>[0-9]+)/add_review/$', views.add_review, name='add_review'),
    ]