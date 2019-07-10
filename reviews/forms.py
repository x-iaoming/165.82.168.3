from django.forms import ModelForm, Textarea
from reviews.models import Review, Restaurant, College, Department, Topic, Response, Profile
from django import forms
from django.contrib.auth.models import User
from django_select2.forms import ModelSelect2Widget, Select2MultipleWidget

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['username','college','year']

class ReviewForm(ModelForm):
    class Meta:
        ASSESSMENTS = (
        ('Problem sets','Problem sets'),
        ('Projects','Projects'),
        ('Presentations','Presentations'),
        ('Exams','Exams'),
        ('Papers','Papers')
        )
        model = Review
        fields = ['restaurant','title','user_name','rating','comment','prof_name','diff_level','syllabus','work_load','assessment']
        #fields = ['rating','user_name','prof_name','pre_req','materials','class_size','assessment','work_load','diff_level','comment']
        widgets = {
            'comment': Textarea(attrs={'cols': 40, 'rows': 15}),
            'assessment': Select2MultipleWidget(choices=ASSESSMENTS),
        }
        labels = {
            "restaurant": "Class",
            "user_name": "Anonymous name"
        }
        help_texts = {
            'user_name': 'Want to be anonymous? Use a name different than your username! Be creative!',
        }

    def __init__(self, department, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.fields['restaurant'].queryset = Restaurant.objects.filter(department=department)

class TopicForm(ModelForm):
    class Meta:
        model = Topic
        fields = ['title','username','content']
        help_texts = {
            'username': 'Your desired name to be displayed. If blank, your username will be used.',
        }
        widgets = {
            'content': Textarea(attrs={'cols': 40, 'rows': 5}),
        }

class ResponseForm(ModelForm):
    class Meta:
        model = Response
        fields = ['username','content']
        help_texts = {
            'username': 'Your desired name to be displayed. If blank, your username will be used.',
        }

class DepartmentForm(forms.Form):
    college = forms.ModelChoiceField(
        queryset=College.objects.all(),
        label=u"College",
        widget=ModelSelect2Widget(
            model=College,
            search_fields=['name__icontains'],
        )
    )


class ContentForm(forms.Form):
    CHOICES = (('0','All'),
               ('1','Class Review'),
               ('2','Study Resources'),
               ('3','Inside Jokes'),
               ('4','Career'),
               ('5','Questions'),)
    content = forms.MultipleChoiceField(choices=CHOICES)
    # model = Review
    # fields = ['anonymous','rating',college,restaurant]

class FindReviewForm(forms.Form):
    college = forms.ModelChoiceField(
        queryset=College.objects.all(),
        label=u"College",
        widget=ModelSelect2Widget(
            model=College,
            search_fields=['name__icontains'],
        )
    )

    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        label=u"Department",
        widget=ModelSelect2Widget(
            model=Department,
            search_fields=['name__icontains'],
            dependent_fields={'college': 'college'},
            max_results=500,
        )
    )

class InviteForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['user']


class GeneralReviewForm(forms.Form):
    college = forms.ModelChoiceField(
        queryset=College.objects.all(),
        label=u"College",
        widget=ModelSelect2Widget(
            model=College,
            search_fields=['name__icontains'],
        )
    )

    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        label=u"Department",
        widget=ModelSelect2Widget(
            model=Department,
            search_fields=['name__icontains'],
            dependent_fields={'college': 'college'},
            max_results=500,
        )
    )

    restaurant = forms.ModelChoiceField(
        queryset=Restaurant.objects.all(),
        label=u"Class",
        widget=ModelSelect2Widget(
            model=Restaurant,
            search_fields=['name__icontains'],
            dependent_fields={'department': 'department'},
            max_results=500,
        )
    )

    RATING_CHOICES = (
        (1,'1'),
        (2,'2'),
        (3,'3'),
        (4,'4'),
        (5,'5'),
    )

    ASSESSMENTS = (
        ('Problem sets','Problem sets'),
        ('Projects','Projects'),
        ('Presentations','Presentations'),
        ('Exams','Exams'),
        ('Papers','Papers')
    )

    DIFF_LEVEL = (
        (1,'VeryEasy'),
        (2,'Easy'),
        (3,'Manageable'),
        (4,'Challenging'),
        (5,'Suffocating'),
    )
    
    name = forms.CharField(label=u"Anonymous name",max_length=100,required=False,help_text='To be anonymous, put something different than your username - show your creativity! If blank, your username will be used.')
    rating = forms.ChoiceField(label=u"Recommendation out of 5",choices=RATING_CHOICES)
    prof_name = forms.CharField(label=u"Taken with",help_text='instructor name', max_length=100)
    assessment = forms.MultipleChoiceField(choices=ASSESSMENTS, widget=Select2MultipleWidget,help_text='select all options applicable')
    title = forms.CharField(label=u"This class in one sentence",max_length=50)
    #pre_req = forms.CharField(label=u"Prior knowledge",max_length=100)
    #materials = forms.CharField(label=u"Materials needed",max_length=100)
    work_load = forms.IntegerField(help_text='hours spent outside class per week')
    diff_level = forms.ChoiceField(label=u"Difficulty level",choices=DIFF_LEVEL)
    
    comment = forms.CharField(label=u"Class Feedback",max_length=400,widget=forms.Textarea(attrs={"rows":5, "cols":20}))
    syllabus = forms.FileField(label=u"Upload Syllabus(Optional)",required=False)
# class GeneralReviewForm(forms.ModelForm):
#     class Meta:
#         model = Review
#         fields = ('college','restaurant','anonymous', 'rating')

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['restaurant'].queryset = Restaurant.objects.none()

#         if 'college' in self.data:
#             try:
#                 college_id = int(self.data.get('college'))
#                 self.fields['restaurant'].queryset = Restaurant.objects.filter(college_id=college_id).order_by('name')
#             except (ValueError, TypeError):
#                 pass  # invalid input from the client; ignore and fallback to empty City queryset
#         elif self.instance.pk:
#             self.fields['restaurant'].queryset = self.instance.college.restaurant_set.order_by('name')

    # def __init__(self, *args, **kwargs):
    #     school = kwargs.pop('school','')
    #     super(GeneralReviewForm, self).__init__(Restaurant)
    #     self.fields['school']=forms.ModelChoiceField(queryset=Restaurant.objects.filter(school=school))
   

# class RestaurantForm(ModelForm):
#     class Meta:
#         forms.CharField(widget=forms.SelectDateWidget(years=BIRTH_YEAR_CHOICES))
#         model = Restaurant
#         fields = ['name','school']
#             