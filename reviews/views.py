from django.shortcuts import get_object_or_404, render
from .models import Restaurant, Review, Cluster, College, Department, Topic, Response, Profile
from .forms import ReviewForm, GeneralReviewForm, TopicForm, ResponseForm, ProfileForm, DepartmentForm, ContentForm, FindReviewForm, InviteForm
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .suggestions import update_clusters
from itertools import chain

# from django.views.generic import ListView, CreateView, UpdateView
# from django.urls import reverse_lazy

# class ReviewListView(ListView):
#     model = Review
#     context_object_name = 'review'

# def ReviewCreateView(CreateView):
#     model = Review
#     form_class = GeneralReviewForm
#     success_url = reverse_lazy('review_changelist')

# class ReviewUpdateView(UpdateView):
#     model = Review
#     form_class = GeneralReviewForm
#     return HttpResponseRedirect(reverse_lazy('review_changelist'))

# def load_restaurants(request):
#     restaurant_id = request.GET.get('college')
#     restaurants = Restaurant.objects.filter(college_id=college_id).order_by('name')
#     return render(request, 'restaurant_dropdown_list_options.html', {'restaurants': restaurants})

def invite(request,department_id):
    department = get_object_or_404(Department, pk=department_id)
    if request.user not in department.sub.all():
        return HttpResponseRedirect(reverse('reviews:denied'))
    
    if request.POST: 
        form = InviteForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            if user not in department.sub.all():
                department.sub.add(user)
            return HttpResponseRedirect(reverse('reviews:department_detail',kwargs={'department_id':department.id}))

    form = InviteForm()
    context = {'form':form,
               'department':department}
    print(User.objects.all())
    return render(request,'reviews/invite.html',context)

def denied(request):
    return render(request,'reviews/permission_denied.html',{})

def find_review(request):
    form = FindReviewForm()
    review_list = Review.objects.order_by('-pub_date')
    context = {'form':form,
               'review_list':review_list}
    if request.POST: 
        form = FindReviewForm(request.POST)
        if form.is_valid():
            department = form.cleaned_data['department']
            return HttpResponseRedirect(reverse('reviews:find_review_result',kwargs={'department_id':department.id}))

    return render(request,'reviews/find_review.html',context)

def find_review_result(request,department_id=None):
    form = FindReviewForm()
    department = get_object_or_404(Department, pk=department_id)
    class_list = Restaurant.objects.filter(department = department).order_by('name')
    if request.POST: 
        form = FindReviewForm(request.POST)
        if form.is_valid():
            department = form.cleaned_data['department']
            return HttpResponseRedirect(reverse('reviews:find_review_result',kwargs={'department_id':department.id}))
    
    context = {'form':form,
               'class_list':class_list,
               'department':department}
    return render(request,'reviews/find_review.html',context)

def review_list(request):
    if request.user.is_authenticated:
        latest_review_list = Review.objects.exclude(users_reported=request.user)[:9]
        latest_topic_list = Topic.objects.exclude(users_reported=request.user)[:9]
    else:
        latest_review_list = Review.objects.all()[:9]
        latest_topic_list = Topic.objects.all()[:9]

    result_list = sorted(
        chain(latest_topic_list, latest_review_list),
        key = lambda instance: instance.pub_date, reverse = True)
    
    context = {'result_list':result_list}
    return render(request,'reviews/review_list.html',context)

def review_detail(request,review_id):
    review = get_object_or_404(Review, pk=review_id)
    context = {'review':review}
    
    return render(request,'reviews/review_detail.html',context)

def topic_detail(request,topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    if request.user not in topic.department.sub.all():
        return HttpResponseRedirect(reverse('reviews:denied'))
    topic_response_list = Response.objects.filter(topic=topic_id).order_by('pub_date')
    context = {'topic':topic,
               'topic_response_list':topic_response_list
            }
    
    return render(request,'reviews/topic_detail.html',context)

def restaurant_list(request):
    restaurant_list = Restaurant.objects.order_by('-name')
    context = {'restaurant_list':restaurant_list}
    return render(request, 'reviews/restaurant_list.html',context)

def restaurant_detail(request,restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    form = ReviewForm()
    if request.user.is_authenticated:
        restaurant_review_list = Review.objects.filter(restaurant=restaurant_id).exclude(users_reported=request.user).order_by('-pub_date')
    else: 
        restaurant_review_list = Review.objects.filter(restaurant=restaurant_id).order_by('-pub_date')
    inside = request.user in restaurant.department.sub.all()
    context = {'restaurant_review_list':restaurant_review_list,
               'restaurant':restaurant,
               'inside':inside
            }
    # {'restaurant':restaurant}
    return render(request, 'reviews/restaurant_detail.html', context)





def department_list(request,college_id=None): 
    form = DepartmentForm()
    if request.POST: 
            form = DepartmentForm(request.POST)
            if form.is_valid():
                college = form.cleaned_data['college']
                return HttpResponseRedirect(reverse('reviews:department_list',kwargs={'college_id':college.id}))
    department_list = Department.objects.filter(college=college_id).order_by('name')
    try:
       sub_dept_list = Department.objects.filter(sub=request.user).order_by('name')
    except:
        sub_dept_list = None
    context = {'department_list':department_list,
               'college':College.objects.filter(pk=college_id).get(),
               'form':form,
               'sub_dept_list':sub_dept_list}
    return render(request, 'reviews/department_list.html',context)

def department_list_all(request):
    form = DepartmentForm()
    college = None
    department_list = None
    sub_dept_list = None
    # Logged in
    if request.user.is_authenticated:
        try:
            # Profile completed
            college_id = request.user.profile.college.id
            college = College.objects.filter(pk=college_id).get()
            department_list = Department.objects.filter(college=college_id).order_by('name')
            sub_dept_list = Department.objects.filter(sub=request.user).order_by('name')
        except:
            sub_dept_list = Department.objects.filter(sub=request.user).order_by('name')
            pass

    if request.POST: 
        form = DepartmentForm(request.POST)
        if form.is_valid():
            college = form.cleaned_data['college']
            return HttpResponseRedirect(reverse('reviews:department_list',kwargs={'college_id':college.id}))

    context = {'department_list':department_list,
               'college':college,
               'form':form,
               'sub_dept_list':sub_dept_list}
    return render(request, 'reviews/department_list.html',context)

def department_detail(request,department_id,content='all'):
    department = get_object_or_404(Department, pk=department_id)
    if request.user not in department.sub.all():
        return HttpResponseRedirect(reverse('reviews:denied'))
    # Get topics
    topic_list = Topic.objects.filter(department=department_id)
    # Get classes in dept
    restaurant_list = Restaurant.objects.filter(department=department_id)
    restaurant_review_list = []
    sub = request.user.username in Department.get_subs(department)
    # Get reviews for classes
    for r in restaurant_list:
        restaurant_id = r.id
        if request.user.is_authenticated:
            restaurant_review_list += Review.objects.filter(restaurant=restaurant_id).exclude(users_reported=request.user)
        else: 
            restaurant_review_list += Review.objects.filter(restaurant=restaurant_id)
    # Conditions on what content to display
    # Combine and sort topics and reviews
    result_list = sorted(
        chain(topic_list, restaurant_review_list),
        key = lambda instance: instance.pub_date, reverse = True)
    form = ContentForm()

    context = {'result_list':result_list,
               #'restaurant_list': restaurant_list,
               'department':department,
               'sub':sub,
               'form':form
            }

    # Form to filter
    if request.POST:
        form = ContentForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content'][0]
            if content == '1':
                context['result_list'] = restaurant_review_list
                return render(request,'reviews/department_detail.html', context)
            elif content == '0':
                return render(request, 'reviews/department_detail.html', context)


    return render(request, 'reviews/department_detail.html', context)

def sub_dept(request, department_id):
    dept = get_object_or_404(Department, pk=department_id)
    if request.user in dept.sub.all():
    #if review in request.user.userprofile.report_review_set.all():
        # next = request.POST.get('next', '/')
        # return HttpResponseRedirect(next)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        dept.sub.add(request.user)
        # next = request.POST.get('next', '/')
        # return HttpResponseRedirect(next)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def unsub_dept(request, department_id):
    dept = get_object_or_404(Department, pk=department_id)
    if request.user in dept.sub.all():
    #if review in request.user.userprofile.report_review_set.all():
        # next = request.POST.get('next', '/')
        # return HttpResponseRedirect(next)
        dept.sub.remove(request.user)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        # next = request.POST.get('next', '/')
        # return HttpResponseRedirect(next)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))






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

        # Set to anonymous if it's requested
        if form.cleaned_data['anonymous']:
            user_name = 'anonymous_users'
        else:
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
def user_profile(request,username=None):
    if not username:
        username = request.user.username
        return HttpResponseRedirect(reverse('reviews:user_profile', kwargs={'username':username})) 
    
    latest_review_list = Review.objects.filter(user_name=username).order_by('-pub_date')
    sub_dept_list = Department.objects.filter(sub=request.user).order_by('name')
    topic_list = Topic.objects.filter(user_name=username).order_by('-pub_date')
    user = User.objects.filter(username=username).get()
    profile = Profile.objects.filter(user = user)

    context = {'latest_review_list':latest_review_list,
                'username':username,
                'sub_dept_list':sub_dept_list,
                'topic_list':topic_list,
                'profile':profile,
                }
    form = ProfileForm()
    return render(request,'reviews/user_profile.html',context)

@login_required
def add_profile(request,username=None):
    if not username:
        username = request.user.username

    user = request.user
    # Edit profile
    if Profile.objects.filter(user = user).exists():
        my_record = Profile.objects.filter(user = user).get()
        form = ProfileForm(instance=my_record)
        if request.POST:
            form = ProfileForm(request.POST, instance=my_record)
            if form.is_valid():
                profile = form.save(commit=False) # commit = False means that this instantiate but not save a Review model object
                profile.user = user
                profile.save()
                return HttpResponseRedirect(reverse('reviews:user_profile', kwargs={'username':username}))
    # Add new profile    
    elif request.POST:
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False) # commit = False means that this instantiate but not save a Review model object
            profile.user = user
            profile.save() # save to the DB now       
            return HttpResponseRedirect(reverse('reviews:user_profile',kwargs={'username':username}))
    # Display empty form
    else: 
        form = ProfileForm() 

    latest_review_list = Review.objects.filter(user_name=username).order_by('-pub_date')
    sub_dept_list = Department.objects.filter(sub=request.user).order_by('name')
    topic_list = Topic.objects.filter(user_name=username).order_by('-pub_date')
    context = {'latest_review_list':latest_review_list,
                'username':username,
                'sub_dept_list':sub_dept_list,
                'topic_list':topic_list,
                'form':form
                }

    return render(request, 'reviews/user_profile.html', context)

@login_required
def add_topic(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    if request.POST:
        form = TopicForm(request.POST)
    else:
        form = TopicForm()  
    if form.is_valid():
        ### NO NEED FOR - already set as part of valid modelform ::: rating = form.cleaned_data['rating']
        ### AS WELL AS ::: comment = form.cleaned_data['comment']

        # Set to anonymous if it's requested
        if form.cleaned_data['anonymous']:
            user_name = 'anonymous_users'
        else:
            user_name = request.user.username

        #user_name = request.user.username
        topic = form.save(commit=False) # commit = False means that this instantiate but not save a Review model object
        topic.department = department
        topic.user_name = user_name # Why use this instead of a ForeignKey to user?
        topic.pub_date = datetime.datetime.now() # works as long as pub_date is a DateTimeField
        topic.save() # save to the DB now       
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('reviews:department_detail', kwargs={'department_id':department_id}))
    
    return render(request, 'reviews/add_topic.html', {'department': department, 'form': form})

@login_required
def add_response(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    if request.POST:
        form = ResponseForm(request.POST)
    else:
        form = ResponseForm()  
    if form.is_valid():
        ### NO NEED FOR - already set as part of valid modelform ::: rating = form.cleaned_data['rating']
        ### AS WELL AS ::: comment = form.cleaned_data['comment']

        # Set to anonymous if it's requested
        if form.cleaned_data['anonymous']:
            user_name = 'anonymous_users'
        else:
            user_name = request.user.username

        #user_name = request.user.username
        response = form.save(commit=False) # commit = False means that this instantiate but not save a Review model object
        response.topic = topic
        response.user_name = user_name # Why use this instead of a ForeignKey to user?
        response.pub_date = datetime.datetime.now() # works as long as pub_date is a DateTimeField
        response.save() # save to the DB now       
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('reviews:topic_detail', kwargs={'topic_id':topic_id}))
    
    return render(request, 'reviews/topic_detail.html', {'topic': topic, 'form': form})

def add_general_review(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')
    form=GeneralReviewForm()
    if request.POST:
        form = GeneralReviewForm(request.POST)
        if form.is_valid():

            if form.cleaned_data['anonymous']:
                user_name = 'anonymous_users'
            else:
                user_name = request.user.username
            
            college = College.objects.filter(name = form.cleaned_data['college']).get()
            department = Department.objects.filter(college = college).filter(name = form.cleaned_data['department']).get()
            restaurant = Restaurant.objects.filter(department = department).filter(name = form.cleaned_data['restaurant']).get()

            lst = form.cleaned_data['assessment']
            assessment = ''
            for item in lst:
                assessment = assessment + item + ' '

            review = Review(
            pub_date= datetime.datetime.now(),
            user_name = user_name,
            rating = form.cleaned_data['rating'],
            prof_name = form.cleaned_data['prof_name'],
            assessment = assessment,
            class_size = form.cleaned_data['class_size'],
            materials = form.cleaned_data['materials'],
            pre_req = form.cleaned_data['pre_req'],
            work_load = form.cleaned_data['work_load'],
            diff_level = form.cleaned_data['diff_level'])
            review.restaurant = restaurant
            review.save()
            department.sub.add(request.user)
            

            return HttpResponseRedirect(reverse('reviews:restaurant_detail', kwargs={'restaurant_id':restaurant.id}))
    
    context = { 'form':form }

    return render(request,'reviews/add_general_review.html', context)

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if review.user_name != request.user.username:
        return HttpResponseForbidden()

    form = ReviewForm(request.POST or None, instance=review)
    if request.POST and form.is_valid():
        form.save()

        # Save was successful, so redirect to another page
        # next = request.POST.get('next', '/')
        # return HttpResponseRedirect(next)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

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
    # next = request.POST.get('next', '/')
    # return HttpResponseRedirect(next)
    return HttpResponseRedirect(reverse('reviews:user_profile'))
    # return render(request, 'reviews/edit_review.html', {
    #     'review': review,
    #     'form': form
    # })

@login_required
def report_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if request.user in review.users_reported.all():
    #if review in request.user.userprofile.report_review_set.all():
        # next = request.POST.get('next', '/')
        # return HttpResponseRedirect(next)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        review.users_reported.add(request.user)
        if review.get_report_counts() >= 5:
            review.delete()
        # next = request.POST.get('next', '/')
        # return HttpResponseRedirect(next)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def like_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if request.user in review.users_liked.all():
    #if review in request.user.userprofile.report_review_set.all():
        # next = request.POST.get('next', '/')
        # return HttpResponseRedirect(next)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        review.users_liked.add(request.user)
        # next = request.POST.get('next', '/')
        # return HttpResponseRedirect(next)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def edit_topic(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    if topic.user_name != request.user.username:
        return HttpResponseForbidden()

    form = ReviewForm(request.POST or None, instance=topic)
    if request.POST and form.is_valid():
        form.save()

        # Save was successful, so redirect to another page
        # next = request.POST.get('next', '/')
        # return HttpResponseRedirect(next)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    return render(request, 'reviews/edit_topic.html', {
        'topic': topic,
        'form': form
    })

@login_required
def delete_topic(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    user_name = review.user_name
    if user_name != request.user.username:
        return HttpResponseForbidden()

    topic.delete()
    # next = request.POST.get('next', '/')
    # return HttpResponseRedirect(next)
    return HttpResponseRedirect(reverse('reviews:user_profile'))
    # return render(request, 'reviews/edit_review.html', {
    #     'review': review,
    #     'form': form
    # })

@login_required
def report_topic(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    if request.user in topic.users_reported.all():
    #if review in request.user.userprofile.report_review_set.all():
        # next = request.POST.get('next', '/')
        # return HttpResponseRedirect(next)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        topic.users_reported.add(request.user)
        if topic.get_report_counts() >= 5:
            topic.delete()
        # next = request.POST.get('next', '/')
        # return HttpResponseRedirect(next)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def like_topic(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    if request.user in topic.users_liked.all():
    #if review in request.user.userprofile.report_review_set.all():
        # next = request.POST.get('next', '/')
        # return HttpResponseRedirect(next)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        topic.users_liked.add(request.user)
        # next = request.POST.get('next', '/')
        # return HttpResponseRedirect(next)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



# def user_review_list(request,username=None):
#     if not username:
#         username = request.user.username

#     # Users have to complete their profile first
#     # Change to mandatory fields and no need to check college and year separately
#     profile = Profile.objects.filter(user=request.user)
#     form = ProfileForm()
#     if profile.exists():
#         profile_completed = profile.get().college != None and profile.get().year != None
#     else:
#         profile_completed = False

#     latest_review_list = Review.objects.filter(user_name=username).order_by('-pub_date')
#     sub_dept_list = Department.objects.filter(sub=request.user).order_by('name')
#     topic_list = Topic.objects.filter(user_name=username).order_by('-pub_date')
    
#     context = {'latest_review_list':latest_review_list,
#                 'username':username,
#                 'sub_dept_list':sub_dept_list,
#                 'topic_list':topic_list,
#                 'profile_completed':profile_completed}
#     return render(request,'reviews/user_review_list.html',context)

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