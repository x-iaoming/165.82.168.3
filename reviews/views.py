from django.shortcuts import get_object_or_404, render
from .models import Restaurant, Review, Cluster
from .forms import ReviewForm
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .suggestions import update_clusters

def review_list(request):
    if request.user.is_authenticated:
        latest_review_list = Review.objects.exclude(users_reported=request.user).order_by('-pub_date')[:9]
    else:
        latest_review_list = Review.objects.order_by('-pub_date')[:9]
    context = {'latest_review_list':latest_review_list}
    return render(request,'reviews/review_list.html',context)

def review_detail(request,review_id):
    review = get_object_or_404(Review, pk=review_id)
    context = {'review':review}
    
    return render(request,'reviews/review_detail.html',context)

def restaurant_list(request):
    restaurant_list = Restaurant.objects.order_by('-name')
    context = {'restaurant_list':restaurant_list}
    return render(request, 'reviews/restaurant_list.html',context)

def restaurant_detail(request,restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    form = ReviewForm()
    if request.user.is_authenticated:
        restaurant_review_list = Review.objects.filter(restaurant=restaurant_id).exclude(users_reported=request.user)
    else: 
        restaurant_review_list = Review.objects.filter(restaurant=restaurant_id)
    context = {'restaurant_review_list':restaurant_review_list,
               'restaurant':restaurant
            }
    # {'restaurant':restaurant}
    return render(request, 'reviews/restaurant_detail.html', context)

@login_required
def add_review(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    if request.POST:
        form = ReviewForm(request.POST)
    else:
        form = ReviewForm()  
    if form.is_valid():
        ### NO NEED FOR - already set as part of valid modelform ::: rating = form.cleaned_data['rating']
        ### AS WELL AS ::: comment = form.cleaned_data['comment']

        ### THIS IS NOT A FIELD IN YOUR FORM :::
        #user_name = form.cleaned_data['user_name']
        user_name = request.user.username
        #user_name = request.user.username
        review = form.save(commit=False) # commit = False means that this instantiate but not save a Review model object
        review.restaurant = restaurant
        review.user_name = user_name # Why use this instead of a ForeignKey to user?
        review.pub_date = datetime.datetime.now() # works as long as pub_date is a DateTimeField
        review.save() # save to the DB now
        update_clusters()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('reviews:restaurant_detail', kwargs={'restaurant_id':restaurant_id}))
    
    return render(request, 'reviews/restaurant_detail.html', {'restaurant': restaurant, 'form': form})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if review.user_name != request.user.username:
        return HttpResponseForbidden()

    form = ReviewForm(request.POST or None, instance=review)
    if request.POST and form.is_valid():
        form.save()

        # Save was successful, so redirect to another page
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

    return render(request, 'reviews/edit_review.html', {
        'review': review,
        'form': form
    })

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    user_name = review.user_name
    if user_name != request.user.username:
        return HttpResponseForbidden()

    review.delete()
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next)

    # return render(request, 'reviews/edit_review.html', {
    #     'review': review,
    #     'form': form
    # })

@login_required
def report_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if request.user in review.users_reported.all():
    #if review in request.user.userprofile.report_review_set.all():
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)
    else:
        review.users_reported.add(request.user)
        if review.get_report_counts() >= 5:
            review.delete()
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


def user_review_list(request,username=None):
    if not username:
        username = request.user.username
    latest_review_list = Review.objects.filter(user_name=username).order_by('-pub_date')
    context = {'latest_review_list':latest_review_list,'username':username}
    return render(request,'reviews/user_review_list.html',context)

@login_required
def user_recommendation_list(request):
    # get this user reviews
    user_reviews = Review.objects.filter(user_name=request.user.username).prefetch_related('restaurant')
    # from the reviews, get a set of restaurant IDs
    user_reviews_restaurant_ids = set(map(lambda x: x.restaurant.id, user_reviews))

    try:
        user_cluster_name = \
            request.user.cluster_set.first().name
    except: # if no cluster has been assigned for a user, update clusters
        update_clusters()
        user_cluster_name = \
            request.user.cluster_set.first().name

    user_cluster_other_members = \
        Cluster.objects.get(name=user_cluster_name).users \
            .exclude(username=request.user.username).all()
    other_members_usernames = set(map(lambda x: x.username, user_cluster_other_members))


    other_users_reviews = \
        Review.objects.filter(user_name__in=other_members_usernames) \
            .exclude(restaurant_id__in=user_reviews_restaurant_ids)
    other_users_reviews_restaurant_ids = set(map(lambda x: x.restaurant.id, other_users_reviews))

    # then get a restaurant list excluding the previous IDs
    restaurant_list = sorted(
        list(Restaurant.objects.filter(id__in=other_users_reviews_restaurant_ids)), 
        key=Restaurant.average_rating, 
        reverse=True
    )

    return render(
        request, 
        'reviews/user_recommendation_list.html', 
        {'username': request.user.username,'restaurant_list': restaurant_list}
    )