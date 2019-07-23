from django.shortcuts import get_object_or_404, render
from .models import Restaurant, Review, Cluster, College, Department, Topic, Response, Profile
from .forms import ReviewForm, GeneralReviewForm, TopicForm, ResponseForm, ProfileForm, DepartmentForm, ContentForm, FindReviewForm, CollegeForm
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden
from django.urls import reverse
from django.core.paginator import Paginator
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .suggestions import update_clusters
from itertools import chain
from django.db.models import Count
from django.utils import timezone
try:
    from django.utils import simplejson as json
except ImportError:
    import json


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
def redirect(request):
    if request.user.is_authenticated and request.user.profile:
        return HttpResponseRedirect(reverse('reviews:user_recommendation_list'))
    elif request.user.is_authenticated:
        return HttpResponseRedirect(reverse('reviews:add_profile'))
    else:
        return HttpResponseRedirect(reverse('reviews:user_recommendation_list'))
    #     return HttpResponseRedirect(reverse('reviews:latest'))
    # else:
    #     return HttpResponseRedirect(reverse('reviews:review_list'))
    

def add_department(request,user_id):
    college = request.user.profile.college
    department_list = Department.objects.filter(college=college).exclude(sub=request.user).order_by("name")
    count = Department.objects.filter(sub=request.user).count()
    nxt = count >= 4
    count = 4 - count
    context = {"department_list":department_list,
               "nxt":nxt,
               "count":count}
    return render(request,"reviews/add_department.html",context)

def add_a_review(request):
    form=GeneralReviewForm()
    if request.POST:
        form = GeneralReviewForm(request.POST,request.FILES)
        if form.is_valid():
            
            college = College.objects.filter(name = form.cleaned_data['college']).get()
            department = Department.objects.filter(college = college).filter(name = form.cleaned_data['department']).get()


            # lst = form.cleaned_data['assessment']
            # assessment = ''
            # for item in lst:
            #     assessment = assessment + item + ' '
            
            # if form.cleaned_data['name'] == '':
            #     user_name = request.user.profile.username
            # else:
            #     user_name = form.cleaned_data['name']

            # syllabus = None
            # if request.FILES:
            #     syllabus = request.FILES['syllabus']
            

            # Add a class
            restaurant = Restaurant(
            name = form.cleaned_data['restaurant'],
            department = department
            )
            restaurant.save()

            # Add review for the new class
            review = Review(
            pub_date = timezone.now(),
            rating = form.cleaned_data['rating'],
            prof_name = form.cleaned_data['prof_name'],
            comment = form.cleaned_data['comment'])
            review.restaurant = restaurant
            review.user = request.user
            review.restaurant.department.sub.add(request.user) 
            review.save()
   
            return HttpResponseRedirect(reverse('reviews:user_recommendation_list'))
    
    context = { 'form':form }

    return render(request,'reviews/add_a_review.html', context)

def latest(request):
    department_list = None
    if request.user.is_authenticated:
        # review_list = Review.objects.exclude(users_reported=request.user).order_by('-pub_date')
        # department_list = Department.objects.exclude(sub=request.user).order_by('name')
        # for r in review_list:
        #     if r.restaurant.department not in department_list:
        #         review_list.exclude(pk=r.id)

        # topic_list = Topic.objects.order_by('-act_date')
        # for t in topic_list:
        #     if t.department not in department_list:
        #         topic_list.exclude(pk=t.id)
        review_list = User.objects.none()
        topic_list = User.objects.none()
        department_list = Department.objects.filter(sub=request.user).order_by('name')
        user_review_list = Review.objects.filter(user=request.user)
        for d in department_list:
            topic_list = list(chain(topic_list,Topic.objects.filter(department=d)))
            for r in Restaurant.objects.filter(department=d):
                review_list = list(chain(review_list,Review.objects.exclude(users_reported=request.user).filter(restaurant=r)))

    else:
        review_list = Review.objects.order_by('-pub_date')
        topic_list = Topic.objects.order_by('-act_date')
        user_review_list = None

    form = FindReviewForm()
    if request.POST: 
            form = FindReviewForm(request.POST)
            if form.is_valid():
                department = form.cleaned_data['department']
                return HttpResponseRedirect(reverse('reviews:department_list',kwargs={'department_id':department.id}))
    
    result_list = sorted(
        chain(review_list, topic_list),
        key = lambda instance: instance.pub_date, reverse = True)



    restaurants = Restaurant.objects.all()
    most_recommended = sorted(restaurants, key=lambda r: r.average_rating(), reverse=True)[:4]

    most_followed = Department.objects.annotate(q_count=Count('sub')) \
                                 .order_by('-q_count')[:4]
    # most_active = Topic.objects\
    #             .annotate(num_likes=Count('users_liked')) \
    #             .order_by('-num_likes')[:5]
    most_helpful = Review.objects\
                .annotate(num_liked=Count('users_liked')) \
                .order_by('-num_liked')[:4]


    
    paginator = Paginator(result_list, 10)
    page = request.GET.get('page')
    result_list = paginator.get_page(page)

    context = {'result_list':result_list,
               'sub_dept_list':department_list,
               'user_review_list':user_review_list,
               'most_recommended':most_recommended,
               'most_helpful':most_helpful,
               'most_followed':most_followed,
               'form':form}

    return render(request,"reviews/latest.html",context)

def invite(request,department_id):
    department = get_object_or_404(Department, pk=department_id)
    if request.user not in department.sub.all():
        return HttpResponseRedirect(reverse('reviews:denied'))
    
    if request.POST: 
        form = InviteForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            department.sub.add(user)
        return HttpResponseRedirect(reverse('reviews:department_detail',kwargs={'department_id':department.id}))

    form = InviteForm()
    context = {'form':form,
               'department':department}
    print(User.objects.all())
    return render(request,'reviews/invite.html',context)

def denied(request,department_id):
    context = {'department':get_object_or_404(Department,pk=department_id)}
    return render(request,'reviews/permission_denied.html',context)

def find_review(request):
    form = FindReviewForm()
    if request.user.is_authenticated:    
        review_list = Review.objects.exclude(users_reported=request.user).order_by('-pub_date')
    else:
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
               'department':department,}

    return render(request,'reviews/find_review.html',context)

def review_list(request):
    restaurants = Restaurant.objects.all()
    most_recommended = sorted(restaurants, key=lambda r: r.average_rating(), reverse=True)[:5]

    most_followed = Department.objects.annotate(q_count=Count('sub')) \
                                 .order_by('-q_count')[:5]
    most_active = Topic.objects\
                .annotate(num_likes=Count('users_liked')) \
                .order_by('-num_likes')[:5]
    most_helpful = Review.objects\
                .annotate(num_liked=Count('users_liked')) \
                .order_by('-num_liked')[:5]
    most_inside = User.objects\
                .annotate(num_inside=Count('department')) \
                .order_by('-num_inside')[:5]

    form = FindReviewForm()
    if request.POST: 
            form = FindReviewForm(request.POST)
            if form.is_valid():
                department = form.cleaned_data['department']
                return HttpResponseRedirect(reverse('reviews:department_list',kwargs={'department_id':department.id}))
    # if request.user.is_authenticated:
    #     latest_review_list = Review.objects.exclude(users_reported=request.user)[:9]
    #     latest_topic_list = Topic.objects.exclude(users_reported=request.user)[:9]
    # else:
    #     latest_review_list = Review.objects.all()[:9]
    #     latest_topic_list = Topic.objects.all()[:9]

    # result_list = sorted(
    #     chain(latest_topic_list, latest_review_list),
    #     key = lambda instance: instance.pub_date, reverse = True)
    
    context = {'form':form,
               'most_followed':most_followed,
               'most_active':most_active,
               'most_helpful':most_helpful,
               'most_inside':most_inside,
               'most_recommended':most_recommended,
               }
    return render(request,'reviews/review_list.html',context)

def review_detail(request,review_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')
    
    review = get_object_or_404(Review, pk=review_id)
    if request.user not in review.restaurant.department.sub.all():
        return HttpResponseRedirect(reverse('reviews:denied',kwargs={'department_id':review.restaurant.department.id}))
    
    context = {'review':review}
    
    return render(request,'reviews/review_detail.html',context)


def topic_detail(request,topic_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')
    topic = get_object_or_404(Topic, pk=topic_id)
    if request.user not in topic.department.sub.all():
        return HttpResponseRedirect(reverse('reviews:denied',kwargs={'department_id':topic.department.id}))
    topic_response_list = Response.objects.filter(topic=topic_id).order_by('-pub_date')
    context = {'topic':topic,
               'topic_response_list':topic_response_list
            }
    
    return render(request,'reviews/topic_detail.html',context)

def restaurant_list(request):
    restaurant_list = Restaurant.objects.order_by('-name')
    context = {'restaurant_list':restaurant_list}
    return render(request, 'reviews/restaurant_list.html',context)

def restaurant_detail(request,restaurant_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')
    
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    if request.user not in restaurant.department.sub.all():
        return HttpResponseRedirect(reverse('reviews:denied',kwargs={'department_id':restaurant.department.id}))

    form = ReviewForm(restaurant.department)
    restaurant_review_list = Review.objects.filter(restaurant=restaurant_id).exclude(users_reported=request.user).order_by('-pub_date')     
    context = {'restaurant_review_list':restaurant_review_list,
               'restaurant':restaurant,
            }
    # {'restaurant':restaurant}
    return render(request, 'reviews/restaurant_detail.html', context)





def department_list(request,department_id=None): 
    department = get_object_or_404(Department,pk=department_id)
    form = FindReviewForm()
    if request.POST: 
            form = FindReviewForm(request.POST)
            if form.is_valid():
                department = form.cleaned_data['department']
                return HttpResponseRedirect(reverse('reviews:department_list',kwargs={'department_id':department.id}))
    
    sub_dept_list = []
    topic_list = []
    restaurant_review_list = []
    class_list = Restaurant.objects.filter(department=department_id).order_by('name')
    if request.user.is_authenticated:
        sub_dept_list = Department.objects.filter(sub=request.user).order_by('name')    
        topic_list = Topic.objects.filter(department=department_id).order_by('-act_date')
        for r in class_list:
            restaurant_id = r.id
            restaurant_review_list += Review.objects.filter(restaurant=restaurant_id).exclude(users_reported=request.user)
    result_list = sorted(
        chain(topic_list, restaurant_review_list),
        key = lambda instance: instance.pub_date, reverse = True)

    sub = False
    sub_list = None
    if request.user in department.sub.all():
        sub = True
        sub_list = department.sub.all()

    context = {'class_list':class_list,
               'result_list':result_list,
               'sub_dept_list':sub_dept_list,
               'form':form,
               'department':department,
               'sub':sub,
               'sub_list':sub_list}
    return render(request, 'reviews/department_list.html',context)

def department_list_all(request):
    form = FindReviewForm()
    latest_topic_list = Topic.objects.order_by('-act_date')

    if request.POST: 
        form = FindReviewForm(request.POST)
        if form.is_valid():
            department = form.cleaned_data['department']
            return HttpResponseRedirect(reverse('reviews:department_list',kwargs={'department_id':department.id}))

    context = {'latest_topic_list':latest_topic_list,
               'form':form}
    return render(request, 'reviews/department_list.html',context)

def department_detail(request,department_id,content='all'):
    department = get_object_or_404(Department, pk=department_id)
    # if request.user not in department.sub.all():
    #     return HttpResponseRedirect(reverse('reviews:denied'))
    # Get topics
    topic_list = Topic.objects.filter(department=department_id)
    # Get classes in dept
    restaurant_list = Restaurant.objects.filter(department=department_id)
    restaurant_review_list = []
    
    sub = False
    if request.user in department.sub.all():
        sub = True
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
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')
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
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')
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
def add_review(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    if request.POST:
        form = ReviewForm(department,request.POST)
        if form.is_valid() == False:
            print('Trouble')
        if form.is_valid():
        ### NO NEED FOR - already set as part of valid modelform ::: rating = form.cleaned_data['rating']
        ### AS WELL AS ::: comment = form.cleaned_data['comment']

        # Set to anonymous if it's requested
        # if form.cleaned_data['anonymous']:
        #     user_name = 'anonymous_users'
        # else:
        #     user_name = request.user.username

        #user_name = request.user.username
        #restaurant = form.cleaned_data['restaurant']

            review = form.save(commit=False) # commit = False means that this instantiate but not save a Review model object
        # review.restaurant = restaurant
        # review.user_name = user_name # Why use this instead of a ForeignKey to user?
            review.user = request.user
            review.pub_date = timezone.now() # works as long as pub_date is a DateTimeField
            review.save() # save to the DB now       

            update_clusters()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
            return HttpResponseRedirect(reverse('reviews:user_recommendation_list'))
    return HttpResponseRedirect(reverse('reviews:user_recommendation_list'))
    #return render(request, 'reviews/user_recommendation_list.html', {'form': form,'department':department})


def user_profile(request,user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')
    if not user_id:
        user_id = request.user.id
        return HttpResponseRedirect(reverse('reviews:user_profile', kwargs={'user_id':user_id})) 
    user=get_object_or_404(User,pk=user_id)
    latest_review_list = Review.objects.filter(user=user).order_by('-pub_date')
    sub_dept_list = Department.objects.filter(sub=user).order_by('name')
    topic_list = Topic.objects.filter(user=user).order_by('-pub_date')
    profile = Profile.objects.filter(user=user).get()

    context = {'latest_review_list':latest_review_list,
                'user_viewed':user,
                'sub_dept_list':sub_dept_list,
                'topic_list':topic_list,
                'profile':profile,
                }
    form = ProfileForm()
    return render(request,'reviews/user_profile.html',context)

def add_new_profile(request,user_id):
    user = request.user
    if request.POST:
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False) # commit = False means that this instantiate but not save a Review model object
            profile.user = user
            profile.save() # save to the DB now       
            return HttpResponseRedirect(reverse('reviews:redirect'))
    # Display empty form 
    form = ProfileForm() 
    context = {"form":form}

    return render(request,"reviews/add_new_profile.html",context)

def add_profile(request,user_id):
    user = request.user
    # Edit profile
    my_record = Profile.objects.filter(user=user).get()
    form = ProfileForm(instance=my_record)
    if request.POST:
        form = ProfileForm(request.POST, instance=my_record)
        if form.is_valid():
            profile = form.save(commit=False) # commit = False means that this instantiate but not save a Review model object
            profile.user = user
            profile.save()
            return HttpResponseRedirect(reverse('reviews:user_profile', kwargs={'user_id':user.id}))
    # Display empty form
    else: 
        form = ProfileForm() 

    latest_review_list = Review.objects.filter(user=user).order_by('-pub_date')
    sub_dept_list = Department.objects.filter(sub=user).order_by('name')
    topic_list = Topic.objects.filter(user=user).order_by('-pub_date')
    context = {'latest_review_list':latest_review_list,
                'sub_dept_list':sub_dept_list,
                'topic_list':topic_list,
                'form':form,
                'user_viewed':user,
                'profile':None,
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

        if form.cleaned_data['username'] == None:
            user_name = request.user.profile.username
        else:
            user_name = form.cleaned_data['username']

        #user_name = request.user.username
        topic = form.save(commit=False) # commit = False means that this instantiate but not save a Review model object
        topic.department = department
        topic.username = user_name # Why use this instead of a ForeignKey to user?
        topic.save() # save to the DB now       
        topic.user.add(request.user)
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('reviews:department_list', kwargs={'department_id':department_id}))
    
    return render(request, 'reviews/add_topic.html', {'department': department, 'form': form})


def add_response(request, topic_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')
    
    topic = get_object_or_404(Topic, pk=topic_id)
    if request.POST:
        form = ResponseForm(request.POST)
    else:
        form = ResponseForm()  

    if form.is_valid():

        if form.cleaned_data['username'] == None:
            user_name = request.user.profile.username
        else:
            user_name = form.cleaned_data['username']

        response = form.save(commit=False) # commit = False means that this instantiate but not save a Review model object
        response.topic = topic
        response.username = user_name
        response.pub_date = timezone.now() # works as long as pub_date is a DateTimeField
        response.save() # save to the DB now       
        response.user.add(request.user)
        topic.save() # update topic time
        # update latest activity
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('reviews:topic_detail', kwargs={'topic_id':topic_id}))
    
    return render(request, 'reviews/topic_detail.html', {'topic': topic, 'form': form})

def add_general_review(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')
    #form = GeneralReviewForm()
    form = FindReviewForm()
    if request.POST:
        #form = GeneralReviewForm(request.POST,request.FILES)
        form = FindReviewForm(request.POST)
        if form.is_valid():
            department = form.cleaned_data['department']
            return HttpResponseRedirect(reverse('reviews:add_review', kwargs={'department_id':department.id}))

            
            # college = College.objects.filter(name = form.cleaned_data['college']).get()
            # department = Department.objects.filter(college = college).filter(name = form.cleaned_data['department']).get()
            # restaurant = Restaurant.objects.filter(department = department).filter(name = form.cleaned_data['restaurant']).get()

            # lst = form.cleaned_data['assessment']
            # assessment = ''
            # for item in lst:
            #     assessment = assessment + item + ' '
            
            # if form.cleaned_data['name'] == '':
            #     user_name = request.user.profile.username
            # else:
            #     user_name = form.cleaned_data['name']

            # syllabus = None
            # if request.FILES:
            #     syllabus = request.FILES['syllabus']


            # review = Review(
            # pub_date = datetime.datetime.now(),
            # user_name = user_name,
            # rating = form.cleaned_data['rating'],
            # prof_name = form.cleaned_data['prof_name'],
            # assessment = assessment,
            # work_load = form.cleaned_data['work_load'],
            # diff_level = form.cleaned_data['diff_level'],
            # syllabus = syllabus,
            # comment = form.cleaned_data['comment'])
            # review.restaurant = restaurant
            # review.save()
            # review.user.add(request.user) 
            # review.restaurant.department.sub.add(request.user)
            
            # return HttpResponseRedirect(reverse('reviews:restaurant_detail', kwargs={'restaurant_id':restaurant.id}))
    
    context = { 'form':form }

    return render(request,'reviews/add_general_review.html', context)


def edit_review(request, review_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')
    review = get_object_or_404(Review, pk=review_id)
    if review.user != request.user:
        return HttpResponseForbidden()

    form = ReviewForm(department=review.restaurant.department,instance=review)
    if request.POST:
            rating = request.POST['rating']
            review.rating = rating
            prof_name = request.POST['prof_name']
            review.prof_name = prof_name
            comment = request.POST['comment']
            review.comment = comment
            review.save()
        # Save was successful, so redirect to another page
        # next = request.POST.get('next', '/')
        # return HttpResponseRedirect(next)
            return HttpResponseRedirect('/recommendation/')

    return render(request, 'reviews/edit_review.html', {
        'review': review,
        'form': form
    })


def delete_review(request, review_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')
    review = get_object_or_404(Review, pk=review_id)
    if review.user != request.user:
        return HttpResponseForbidden()
    review.delete()
    # next = request.POST.get('next', '/')
    # return HttpResponseRedirect(next)
    return HttpResponseRedirect(reverse('reviews:user_recommendation_list'))
    # return render(request, 'reviews/edit_review.html', {
    #     'review': review,
    #     'form': form
    # })


def report_review(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')
    if request.method == 'POST':
        review_id = request.POST.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        
        if request.user in review.users_reported.all():
    #if review in request.user.userprofile.report_review_set.all():
        # next = request.POST.get('next', '/')
        # return HttpResponseRedirect(next)
            return None
        else:
            review.users_reported.add(request.user)
            if review.get_report_counts() >= 10:
                review.delete()
        # next = request.POST.get('next', '/')
        # return HttpResponseRedirect(next)
    return HttpResponse(json.dumps({}), content_type='application/json')
   
def like_review(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')
    if request.method == 'POST':
        review_id = request.POST.get('review_id')
        review = get_object_or_404(Review, pk=review_id)

        if request.user in review.users_liked.all():
            # user has already liked this company
            # remove like/user
            review.users_liked.remove(request.user)
    
        else:
            # add a new like for a company
            review.users_liked.add(request.user)


    #ctx = {'likes_count': review.get_like_counts}
    # use mimetype instead of content_type if django < 5
    return HttpResponse(json.dumps({}), content_type='application/json')
    #return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    #review = get_object_or_404(Review, pk=review_id)
    ##if request.user in review.users_liked.all():
    #if review in request.user.userprofile.report_review_set.all():
        # next = request.POST.get('next', '/')
        # return HttpResponseRedirect(next)
        ##return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    ##else:
        ##review.users_liked.add(request.user)
        # next = request.POST.get('next', '/')
        # return HttpResponseRedirect(next)
        ##return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    # if request.method == 'GET':
    #            if request.user in review.users_liked.all():
    #                return HttpResponse("Success!")
    #            else:
    #                review.users_liked.add(request.user)
    #                return HttpResponse("Success!") # Sending an success response



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

def like_topic(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')
    if request.method == 'POST':
        topic_id = request.POST.get('topic_id')
        topic = get_object_or_404(Topic, pk=topic_id)

        if request.user in topic.users_liked.all():
            # user has already liked this company
            # remove like/user
            topic.users_liked.remove(request.user)
    
        else:
            # add a new like for a company
            topic.users_liked.add(request.user)


    #ctx = {'likes_count': review.get_like_counts}
    # use mimetype instead of content_type if django < 5
    return HttpResponse(json.dumps({}), content_type='application/json')



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




def user_recommendation_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login/')
    college = request.user.profile.college
    try:
        department=form.cleaned_data['department']
    except:
        department = Department.objects.filter(college=college).first()
    form = FindReviewForm()
    form2 = ReviewForm(department)

    if request.POST:
        #form = GeneralReviewForm(request.POST,request.FILES)
        form = FindReviewForm(request.POST)
        if form.is_valid():
            college = form.cleaned_data['college']
            department = form.cleaned_data['department']
            form = FindReviewForm(initial={'department':department,'college':college})
            form2 = ReviewForm(department)

    latest_review_list = Review.objects.filter(user=request.user).order_by('-pub_date')

    # get this user reviews
    user_reviews = Review.objects.filter(user=request.user).prefetch_related('restaurant')
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
       User.objects.filter(cluster__in=request.user.cluster_set.all())

    other_users_reviews = \
        Review.objects.filter(user__in=user_cluster_other_members) \
            .exclude(restaurant_id__in=user_reviews_restaurant_ids)
    other_users_reviews_restaurant_ids = set(map(lambda x: x.restaurant.id, other_users_reviews))

    # then get a restaurant list excluding the previous IDs
    restaurant_list = sorted(
        list(Restaurant.objects.filter(id__in=other_users_reviews_restaurant_ids)), 
        key=Restaurant.average_rating, 
        reverse=True
    )
    
    count = Review.objects.filter(user=request.user).count()
    restaurant_list = restaurant_list[0:2*count]
    
    context = {'username': request.user.profile.username,
               'restaurant_list': restaurant_list,
               'latest_review_list':latest_review_list,
                'form':form,
                'form2':form2,
                'college':college,
                'department':department}

    return render(
        request, 
        'reviews/user_recommendation_list.html', 
        context
    )