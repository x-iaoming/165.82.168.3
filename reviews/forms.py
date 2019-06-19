from django.forms import ModelForm, Textarea
from reviews.models import Review

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['rating','prof_name','pre_req','materials','class_size',
                'assessment','work_load','diff_level','comment']
        widgets = {
            'comment': Textarea(attrs={'cols': 40, 'rows': 15}),
            'prof_name': Textarea(attrs={'cols': 20, 'rows': 1}),
            'pre_req': Textarea(attrs={'cols': 20, 'rows': 1}),
            'materials': Textarea(attrs={'cols': 20, 'rows': 1}),
        }