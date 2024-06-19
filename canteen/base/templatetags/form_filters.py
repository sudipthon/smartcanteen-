from django import template

register = template.Library()


@register.filter
def get_form(forms, day):
    return forms.get(day)

@register.filter
def multiply(value, arg):
    try:
        return value * arg
    except (ValueError, TypeError):
        return ''
