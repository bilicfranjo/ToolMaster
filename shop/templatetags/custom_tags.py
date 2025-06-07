from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.simple_tag
def make_key(attr_id):
    return f"attr_{attr_id}"
