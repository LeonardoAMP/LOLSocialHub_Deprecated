from django import template
register = template.Library()

@register.filter(name='eeex')
def key(d, key_name):
    return d[key_name]


register.filter('key', key)