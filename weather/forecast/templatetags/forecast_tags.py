from django import template
from django.template.defaultfilters import stringfilter
from django.templatetags.static import static

register = template.Library()

@register.filter
@stringfilter
def yr_symbol(symbol_code: str):
    """
    Converts an yr symbol code such as 'cloudy' into a filepath to the corresponding svg file.

    For information about create custom template tags see:
    https://docs.djangoproject.com/en/4.1/howto/custom-template-tags/
    """
    return static(f'forecast/svg/{symbol_code}.svg')


@register.filter
def percentage(value):
    """
    Formats a float as a percent
    """
    return '{0:.0%}'.format(value/100)