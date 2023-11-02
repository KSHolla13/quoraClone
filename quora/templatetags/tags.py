from django import template
# Create your views here.

register = template.Library()
@register.filter(name='in_category')
def in_category(things, category):
    return things.filter(comment=category)


