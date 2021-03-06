from django.forms import ChoiceField
from scorecard_processor.plugins import base, register
from django.utils.translation import ugettext_lazy as _

class YesNoNAField(ChoiceField):
    name = "Yes / No / N/A choice"
    def __init__(self, *args, **kwargs):
        super(YesNoNAField,self).__init__(*args,**kwargs)
        self.choices = (
                ('',''),
                ('yes',_('Yes')),
                ('no',_('No')),
                ('n/a',_('n/a')),
            )

class YesNoField(ChoiceField):
    name = "Yes / No choice"
    def __init__(self, *args, **kwargs):
        super(YesNoField,self).__init__(*args,**kwargs)
        self.choices = (
                ('',''),
                ('yes',_('Yes')),
                ('no',_('No')),
            )

class Rating(ChoiceField):
    r_min = 0
    r_max = 5
    step = 0.5
    name = "Rating: %s - %s (step: %s)" % (r_min, r_max, step)
    def __init__(self, *args, **kwargs):
        super(Rating,self).__init__(*args,**kwargs)
        self.choices = tuple([(x*self.step, x*self.step) for x in range(self.r_min, int(self.r_max / self.step)+1)])

class RatingInt(Rating):
    step=1
    r_min = 0
    r_max = 5
    name = "Rating: %s - %s (step: %s)" % (r_min, r_max, step)

register.register('input','Choice field','yes_no_choice', YesNoField)
register.register('input','Choice field','yes_no_na_choice', YesNoNAField)
register.register('input','Choice field','rating_0_5_half', Rating)
register.register('input','Choice field','rating_0_5', RatingInt)
