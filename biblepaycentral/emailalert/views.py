from django.core.cache import cache
from django.http import Http404
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from biblepaycentral.proposal.models import Proposal
from biblepaycentral.podc.models import RosettaUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from biblepaycentral.masternodes.models import Masternode
from biblepaycentral.emailalert.models import EMailAlert

@login_required
@require_http_methods(["POST"])
def register_alert(request):
    content_type_id = request.POST.get('content_type_id')
    object_id = request.POST.get('object_id')
    
    watched_models = (Proposal, RosettaUser, Masternode)
    
    # first, we need to check that both values are valid and point to a model
    # we watch
    try:
        ct = ContentType.objects.get_for_id(content_type_id)
    except ContentType.DoesNotExist:
        raise Http404("ContentType not found")
    
    model = ct.model_class()
    if not model in watched_models:
        raise Http404("Model not in watch list")
    
    try:
        obj = model.objects.get(pk=object_id)
    except model.DoesNotExist:
        raise Http404("Object not found")
    
    alert , created= EMailAlert.objects.get_or_create(content_type=ct, object_id=object_id, user=request.user)
    alert.save()
    
    # we reset the cache
    cache.delete('emailalert_cache__' + str(request.user.pk))

    return redirect(request.POST.get('redirect_url'))

@login_required
@require_http_methods(["POST"])
def drop_alert(request):
    content_type_id = request.POST.get('content_type_id')
    object_id = request.POST.get('object_id')

    try:
        alert = EMailAlert.objects.get(content_type_id=content_type_id, object_id=object_id, user=request.user)
    except EMailAlert.DoesNotExist:
        pass
    
    alert.delete()

    # we reset the cache
    cache.delete('emailalert_cache__' + str(request.user.pk))

    return redirect(request.POST.get('redirect_url'))
