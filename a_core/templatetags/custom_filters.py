from django import template

register = template.Library()

@register.filter(is_safe=True)
def euro_symbol(value):
    return f'\u20AC{value}'