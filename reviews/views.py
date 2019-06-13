from django.shortcuts import get_object_or_404, render
from .models import Restaurant, Review
from .forms import ReviewForm
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

def review_list(request):
    latest_review_list = Review.objects.order_by('-pub_date')[:9]
    context = {'latest_review_list':latest_review_list}
    return render(request,'reviews/review_list.html',context)

def review_detail(request,review_id):
    review = get_object_or_404(Review, pk=review_id)
    return render(request,'reviews/review_detail.html',{'review':review})

def restaurant_list(request):
    restaurant_list = Restaurant.objects.order_by('-name')
    context = {'restaurant_list':restaurant_list}
    return render(request, 'reviews/restaurant_list.html',context)

def restaurant_detail(request,restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    form = ReviewForm()
    return render(request, 'reviews/restaurant_detail.html', {'restaurant':restaurant})

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
        user_name = form.cleaned_data['user_name']
        #user_name = request.user.username
        review = form.save(commit=False) # commit = False means that this instantiate but not save a Review model object
        review.restaurant = restaurant
        review.user_name = user_name # Why use this instead of a ForeignKey to user?
        review.pub_date = datetime.datetime.now() # works as long as pub_date is a DateTimeField
        review.save() # save to the DB now
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('reviews:restaurant_detail', kwargs={'restaurant_id':restaurant_id}))
    
    return render(request, 'reviews/restaurant_detail.html', {'restaurant': restaurant, 'form': form})