from django import template

register = template.Library()

@register.filter(name='indent')
def indent(value, arg=1):
    import re
    regex = re.compile("^", re.M)
    return re.sub(regex, "\t"*int(arg), value)