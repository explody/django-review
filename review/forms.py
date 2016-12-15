"""Forms for the ``review`` app."""
import re
from django import forms
from django.apps import apps
from django.conf import settings
from django.utils.translation import get_language
from django.contrib.contenttypes.models import ContentType
from django_libs.loaders import load_member

from hvad.forms import TranslatableModelForm

from .models import Review, Rating, RatingCategory, \
    ReviewContentFilter, RatingCategoryChoice

class ReviewAdminForm(forms.ModelForm):

    reviewed_item = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(ReviewAdminForm, self).__init__(*args, **kwargs)
        review = kwargs['instance']

        object_choices = []
        act = getattr(review.content_filter,'allowed_content_types', None)
        if act is None:
            ac = apps.get_app_config('review')
            act = [ct[0] for ct in ac.cts]

        for ctid in act:
            ct = ContentType.objects.get(pk=ctid)

            if ct.model_class() is None:
                continue

            for cto in ContentType.get_all_objects_for_this_type(ct):

                try:
                    obj_id = cto.id
                except AttributeError:
                    continue

                form_value = "type:%s-id:%s" % (ctid, obj_id)
                display_text = "%s - %s" % (getattr(ct.model_class(),
                                                    '__name__',
                                                    ct.name),
                                            cto)

                object_choices.append([form_value, display_text])

                if review.content_type == ct and review.object_id == obj_id:
                    self.fields['reviewed_item'].initial = form_value

        self.fields['reviewed_item'].choices = object_choices


    def save(self, *args, **kwargs):

        object_string = self.cleaned_data['reviewed_item']

        matches = re.match("type:(\d+)-id:(\d+)", object_string).groups()
        content_type_id = matches[0]  # get 45 from "type:45-id:38"
        object_id = matches[1]  # get 38 from "type:45-id:38"

        self.cleaned_data['content_type_id'] = content_type_id
        self.cleaned_data['object_id'] = object_id

        self.instance.object_id = object_id
        self.instance.content_type_id = content_type_id

        return super(ReviewAdminForm, self).save(*args, **kwargs)

    class Meta:
        model = Review
        fields = ('content_filter',
                  'reviewed_item',
                  'content',
                  'language',
                  'creation_date',
                  'last_updated',
                  'average_rating')


class ReviewContentFilterAdminForm(forms.ModelForm):

    class Meta:
        model = ReviewContentFilter
        fields = ('__all__')


class ReviewForm(forms.ModelForm):
    def __init__(self, reviewed_item, user=None, *args, **kwargs):
        self.user = user
        self.reviewed_item = reviewed_item
        self.widget = load_member(
            getattr(settings, 'REVIEW_FORM_CHOICE_WIDGET',
                    'django.forms.widgets.Select')
        )()
        super(ReviewForm, self).__init__(*args, **kwargs)
        # Dynamically add fields for each rating category
        for category in RatingCategory.objects.all():
            field_name = 'category_{0}'.format(category.pk)
            choices = category.get_choices()
            self.fields[field_name] = forms.ChoiceField(
                choices=choices, label=category.name,
                help_text=category.question,
                widget=self.widget,
            )
            self.fields[field_name].required = category.required
            if self.instance.pk:
                try:
                    self.initial.update({
                        'category_{0}'.format(category.pk): Rating.objects.get(
                            review=self.instance, category=category).value,
                    })
                except Rating.DoesNotExist:
                    pass

    def save(self, *args, **kwargs):
        if not self.instance.pk:
            self.instance.user = self.user
            self.instance.reviewed_item = self.reviewed_item
            self.instance.language = get_language()
        self.instance = super(ReviewForm, self).save(*args, **kwargs)
        # Update or create ratings
        for field in self.fields:
            if field.startswith('category_'):
                rating, created = Rating.objects.get_or_create(
                    review=self.instance,
                    category=RatingCategory.objects.get(
                        pk=field.replace('category_', '')),
                )
                rating.value = self.cleaned_data[field]
                rating.save()

        self.instance.average_rating = self.instance.get_average_rating()
        self.instance.save()
        return self.instance

    class Meta:
        model = Review
        fields = ('content', )

class RatingCategoryChoiceInlineForm(TranslatableModelForm):

    def __init__(self, *args, **kwargs):
        super(RatingCategoryChoiceInlineForm, self).__init__(*args, **kwargs)

    class Meta:
        model = RatingCategoryChoice
        fields = ('ratingcategory', 'value', 'label')