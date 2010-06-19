from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = patterns('',
    url(r"^xmapper/$", views.index, name="xmapper")
)
