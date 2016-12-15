from django.apps import AppConfig
from .multiselect import ReviewMultiSelectField


class ReviewConfig(AppConfig):

    name = 'review'

    def ready(self):

        from django.contrib.contenttypes.models import ContentType

        ReviewContentFilter = self.get_model('ReviewContentFilter')
        self.cts = ((ct.id, getattr(ct.model_class(), '__name__', ct.name))
               for ct in ContentType.objects.all())

        self.cts = sorted(self.cts, key=lambda x: x[1])

        allowed_content_types = ReviewMultiSelectField(choices=self.cts)
        allowed_content_types.contribute_to_class(ReviewContentFilter,
                                                  'allowed_content_types')

