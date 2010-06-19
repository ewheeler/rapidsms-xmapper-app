from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings

from rapidsms.utils import render_to_response
from .models import XLoc

@require_GET
def index(req): 
    xlocs = XLoc.objects.all()
    breadcrumbs = (('Map', ''),)
    return render_to_response(req, "xmapper/dashboard.html", { 'xlocs': xlocs, 'breadcrumbs': breadcrumbs } )

