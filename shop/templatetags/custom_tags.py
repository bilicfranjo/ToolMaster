from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.simple_tag
def make_key(attr_id):
    return f"attr_{attr_id}"


@register.simple_tag
def url_without_param(request, param):
    querydict = request.GET.copy()
    querydict.pop(param, None)
    return querydict.urlencode()