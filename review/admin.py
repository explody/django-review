"""Admin classes for the review app."""
from django.contrib import admin
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from hvad.admin import TranslatableAdmin

from . import models
from .forms import ReviewAdminForm, \
    ReviewContentFilterAdminForm, \
    RatingCategoryChoiceInlineForm


# Inline classes

class ReviewRatingInline(admin.TabularInline):
    model = models.Rating


class ReviewExtraInfoInline(admin.TabularInline):
    model = models.ReviewExtraInfo
    list_display = ['type', 'review', 'content_object']


class RatingCategoryChoiceInline(admin.StackedInline):
    model = models.RatingCategoryChoice
    form = RatingCategoryChoiceInlineForm

# Admin classes

class RatingAdmin(admin.ModelAdmin):
    list_display = ['review', 'category', 'value', ]
    raw_id_fields = ['review', ]


class ReviewContentFilterAdmin(admin.ModelAdmin):
    form = ReviewContentFilterAdminForm


class ReviewAdmin(admin.ModelAdmin):

    list_display = ['reviewed_item_ref',
                    'content_filter',
                    'user',
                    'creation_date',
                    'last_updated']

    readonly_fields = ('creation_date','last_updated')

    inlines = [
        ReviewRatingInline,
        ReviewExtraInfoInline
    ]

    form = ReviewAdminForm

    def reviewed_item_ref(self,obj):
        itype = str(ContentType.objects.get_for_model(obj.reviewed_item))
        return '{0}::{1}'.format(itype[0].upper() + itype[1:],
                                 obj.reviewed_item)


class RatingCategoryChoiceAdmin(TranslatableAdmin):

    list_display = ['ratingcategory', 'value', 'get_label']
    list_select_related = []

    def get_label(self, obj):
        return obj.label
    get_label.short_description = _('Label')


class RatingCategoryAdmin(admin.ModelAdmin):
    inlines = [
        RatingCategoryChoiceInline
    ]

admin.site.register(models.Rating, RatingAdmin)
admin.site.register(models.RatingCategoryChoice, RatingCategoryChoiceAdmin)
admin.site.register(models.RatingCategory, RatingCategoryAdmin)
admin.site.register(models.ReviewContentFilter, ReviewContentFilterAdmin)
admin.site.register(models.Review, ReviewAdmin)


