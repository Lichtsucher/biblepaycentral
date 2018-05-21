from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from biblepaycentral.emailalert.models import EMailAlert

def emailalert_exist(content_type_id, object_id, user):
    """ Checks if a specific object is in the email alert list. This
    function is called a lot, so we work with a cached list of the email alerts """
    
    # first we need to get OR create the email alert list for one user
    cached_list = cache.get('emailalert_cache__' + str(user.pk))
    if cached_list is None:
        alerts = EMailAlert.objects.filter(user=user)
        
        cached_list = []
        for alert in alerts:
            cached_list.append([alert.content_type_id, alert.object_id])

        cache.set('emailalert_cache__' + str(user.pk), cached_list, 300)

    # we return true if the requested object is in the alert list for this user
    for entry in cached_list:
        if str(entry[0]) == str(content_type_id) and str(entry[1]) == str(object_id):
            return True
        
    return False
        