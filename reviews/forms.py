from django.forms import ModelForm, Textarea
from reviews.models import Review, Restaurant, College, Department, Topic, Response, Profile
from django import forms
from django.contrib.auth.models import User
from django_select2.forms import ModelSelect2Widget, Select2MultipleWidget

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['college','year']

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['anonymous','rating','prof_name','pre_req','materials','class_size','assessment','work_load','diff_level','comment']
        widgets = {
            'comment': Textarea(attrs={'cols': 40, 'rows': 15}),
            'prof_name': Textarea(attrs={'cols': 20, 'rows': 1}),
            'pre_req': Textarea(attrs={'cols': 20, 'rows': 1}),
            'materials': Textarea(attrs={'cols': 20, 'rows': 1}),
        }

class TopicForm(ModelForm):
    class Meta:
        model = Topic
        fields = ['anonymous','title','content']

class ResponseForm(ModelForm):
    class Meta:
        model = Response
        fields = ['anonymous','content']

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

    ANONY = (
        (False,'False'),
        (True,'True:Your username is NOT recorded.You CANNOT modify this review later!!'),
    )
    
    anonymous = forms.ChoiceField(choices=ANONY)
    rating = forms.ChoiceField(choices=RATING_CHOICES)
    prof_name = forms.CharField(max_length=100)
    assessment = forms.MultipleChoiceField(choices=ASSESSMENTS, widget=Select2MultipleWidget,help_text='select all options applicable')
    class_size = forms.IntegerField()
    pre_req = forms.CharField(label=u"Prior knowledge",max_length=100)
    materials = forms.CharField(max_length=100)
    work_load = forms.IntegerField(help_text='hours spent outside class per week')
    diff_level = forms.ChoiceField(label=u"Difficulty level",choices=DIFF_LEVEL)
    comment = forms.CharField(max_length=400)
    
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