from multiselectfield import MultiSelectField, MultiSelectFormField
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.text import capfirst

class ReviewMultiSelectFormField(MultiSelectFormField):

    widget = FilteredSelectMultiple('',True)

    def __init__(self, *args, **kwargs):
        super(ReviewMultiSelectFormField, self).__init__(*args, **kwargs)
        self.__class__.widget = FilteredSelectMultiple(kwargs['label'], True)


class ReviewMultiSelectField(MultiSelectField):

    def __init__(self, *args, **kwargs):
        super(ReviewMultiSelectField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'required': not self.blank,
                    'label': capfirst(self.verbose_name),
                    'help_text': self.help_text,
                    'choices': self.choices,
                    'max_length': self.max_length,
                    'max_choices': self.max_choices}
        if self.has_default():
            defaults['initial'] = self.get_default()
        defaults.update(kwargs)
        return ReviewMultiSelectFormField(**defaults)