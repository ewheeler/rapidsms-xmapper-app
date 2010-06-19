#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=5

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models
from xforms.models import XForm, XFormSubmission
from xforms.models import xform_received

class XLoc(models.Model):
    submission = models.ForeignKey(XFormSubmission)
    place = models.ForeignKey('Place')

    def __unicode__(self):
        return "%s form from %s" % (self.submission.xform.keyword, self.place.name)

    @property
    def keyword(self):
        if self.submission is not None:
            if self.submission.xform is not None:
                if self.submission.xform.keyword is not None:
                    return self.submission.xform.keyword
    @property
    def lat(self):
        if self.place is not None:
            if self.place.point is not None:
                if self.place.point.latitude is not None:
                    return self.place.point.latitude
        return "" 

    @property
    def lng(self):
        if self.place is not None:
            if self.place.point is not None:
                if self.place.point.longitude is not None:
                    return self.place.point.longitude
        return "" 

class Place(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    slug = models.CharField(max_length=30, blank=True, null=True,
        help_text="An URL-safe alternative to the <em>plural</em> field.")

    point = models.ForeignKey('Point', blank=True, null=True)
    category = models.ManyToManyField('Category', blank=True, null=True)

    def __unicode__(self):
        return self.name

    @classmethod
    def find_by_slug(klass, string):
        place = None
        try:
            place = klass.objects.get(slug__iexact=string)
        except MultipleObjectsReturned:
            #TODO do something?
            pass 
        except ObjectDoesNotExist:
            places = klass.objects.filter(slug__istartswith=string)
            if places.count() == 1:
                return places[0]
            else:
                return None

class Category(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.name

class Point(models.Model):
    """
    This model represents an anonymous point on the globe. It should be
    replaced with something from GeoDjango soon, but I can't seem to get
    Spatialite to build right now...
    """

    latitude  = models.DecimalField(max_digits=13, decimal_places=10)
    longitude = models.DecimalField(max_digits=13, decimal_places=10)

    def __unicode__(self):
        return "%s, %s" % (self.latitude, self.longitude)

# TODO is this the best place for this?? 
def handle_submission(sender, **args):
    submission = args['submission']
    xform = args['xform']

    if not submission.has_errors:
        keyword = xform.keyword

        sub_vals = list(submission.values.all())
        captions = [s.field.caption for s in sub_vals]
        values = [s.value for s in sub_vals]

        sub_dict = dict(zip(captions, values))

        if "location" in sub_dict:
            place = Place.find_by_slug(sub_dict["location"]) 
            if place is not None:
                print place
                #create XLoc
                xloc = XLoc.objects.create(xform=submission, place=place)


# then wire it to the xform_received signal
xform_received.connect(handle_submission)
