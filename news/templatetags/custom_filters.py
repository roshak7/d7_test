from django import template

register = template.Library()


@register.filter(name='censor')
def censor(text, swearing):
    if swearing in text:
        return text.replace(swearing, '***')
    return text
