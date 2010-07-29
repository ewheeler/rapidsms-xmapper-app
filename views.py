import csv
import random

from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import redirect, get_object_or_404, render_to_response
from django.template import RequestContext
from django.conf import settings

from .models import XLoc, Place

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
    return render_to_response("xmapper/dashboard.html",
        { 'xlocs_by_key': xlocs_by_key, 'breadcrumbs': breadcrumbs },
        context_instance=RequestContext(req))

def export_for_heatmap(req):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=team_1_disp_under5.csv'
    #response['Content-Disposition'] = 'attachment; filename=team_1_disp_6_to_14.csv'

    writer = csv.writer(response)

    xlocs = XLoc.objects.filter(group__name="all")
    #xlocs = Place.objects.all()

    for xloc in xlocs:
        sub_dict = xloc.submitted_data
        data = int(sub_dict["disp_under5"])
        #data = int(sub_dict["disp_6_to_14"])

        for times in range(data):
            writer.writerow([xloc.lat, xloc.lng])
        #for times in range(random.randrange(0, 100), random.randrange(100,5000)):
        #    writer.writerow([xloc.point.latitude, xloc.point.longitude])
    return response
