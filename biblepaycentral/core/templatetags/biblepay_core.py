import requests
from django import template

register = template.Library()

@register.simple_tag
def current_biblepay_version():
    version = '0.0.0.0'
    try:
        r = requests.get('http://pool.biblepay.org/SAN/version.htm')
        version = r.content
    except:
        pass

    return version
