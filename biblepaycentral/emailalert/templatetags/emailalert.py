import requests
from django import template
from django.urls import reverse
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.safestring import mark_safe
from biblepaycentral.emailalert.tools import emailalert_exist

register = template.Library()

@register.simple_tag(takes_context=True)
def register_alert_button(context, content_type_id, object_id, return_url):
    
    request = context['request']
    
    # if no user is logged in, we do not allow to add alerts
    if not request.user.is_authenticated:
        return mark_safe('<img src="%s" />' % static('bell_gray.png'))
    
    csrf_token = context.get('csrf_token', '')
    return_url = reverse(return_url)
    target_url = reverse('emailalert_register_alert')
    bell_icon = static('bell.png')
    
    # check if this entry is already in the EmailAlert list
    if emailalert_exist(content_type_id, object_id, request.user):
        target_url = reverse('emailalert_drop_alert')
        bell_icon = static('bell_off.png')
    
    form_string = """<form action="{target_url}" method="POST">
          <input type='hidden' name='csrfmiddlewaretoken' value='{csrf_token}' />
          <input type="hidden" name="content_type_id" value="{content_type_id}" />
          <input type="hidden" name="object_id" value="{object_id}" />
          <input type="hidden" name="redirect_url" value="{return_url}" />
          <input type="image" src="{bell_icon}" alt="Alert" />
        </form>"""     
    
    form_string = form_string.format(
        target_url=target_url,
        csrf_token=str(csrf_token),
        content_type_id=str(content_type_id),
        object_id=object_id,
        return_url=return_url,
        bell_icon=bell_icon,
        )
    
    return mark_safe(form_string)
