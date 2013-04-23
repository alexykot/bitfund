from decimal import Decimal, ROUND_DOWN
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def upto(value, delimiter=None):
    return value.split(delimiter)[0]

@register.filter
@stringfilter
def fract2int(value):
    value = Decimal(value)
    fractional_part = value-value.quantize(Decimal('0'), rounding=ROUND_DOWN)
    fractional_part = str(fractional_part)[2:]
    return fractional_part

upto.is_safe = True

