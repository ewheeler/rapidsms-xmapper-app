from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings

from rapidsms.utils import render_to_response
from .models import XLoc

@require_GET
def index(req): 
    xlocs = XLoc.objects.all()
    keys = []
    for xloc in xlocs:
        if xloc.keyword not in keys:
            keys.append(xloc.keyword)

    print keys

    xlocs_by_key = {}
    for key in keys:
        key_matches = []
        for xloc in xlocs:
            if xloc.keyword == key:
                key_matches.append(xloc)
        xlocs_by_key.update({key : key_matches})
    print xlocs_by_key

    breadcrumbs = (('Map', ''),)
    return render_to_response(req, "xmapper/dashboard.html", { 'xlocs_by_key': xlocs_by_key, 'breadcrumbs': breadcrumbs } )
