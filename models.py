#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=5

from decimal import Decimal as D

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models
from xforms.models import XForm, XFormSubmission
from xforms.models import xform_received

class XLoc(models.Model):
    """ Represents an XForm submission at a particular location (place)
        and optionally a related Group for marker organization purposes. """
    submission = models.ForeignKey(XFormSubmission)
    place = models.ForeignKey('Place')
    group = models.ForeignKey('Group', blank=True, null=True)

    def __unicode__(self):
        return "%s form from %s" % (self.submission.xform.keyword, self.place.name)

    # convenience methods as properties
    @property
    def color(self):
        if self.group is not None:
            if self.group.color is not None:
                return self.group.get_color_display()
        return "red"

    @property
    def submitted_data(self):
        """ Returns a dict representation of related XForm submission
            e.g., {u'field caption' : u'field value', ...} """
        sub_vals = list(self.submission.values.all())
        captions = [str(s.field.caption) for s in sub_vals]
        values = [str(s.value) for s in sub_vals]

        sub_dict = dict(zip(captions, values))
        return sub_dict

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
    """ Basic representation of a location, called Place as an attempt to
        avoid confusion with Locations app's Location model. """
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
            return place
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
    """ TODO find out if this is useful for anything ... """
    name = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.name

class Group(models.Model):
    """ Simple class for organizing map marker colors/icons.
        These COLOR_CHOICES are the first portion of icon image
        filenames in static/javascripts/openlayers/img/COLOR_CHOICE_marker.png

        To add a new marker, place your png in the above directory and name it
        MYICON_marker.png and add a tuple to the COLOR_CHOICES
        e.g., ('MY', 'MYICON')

        Please be aware that the map marker javascript is expecting 
        21 by 25 pixel icons, so yours might get warped. 
        Offending code is marked with a TODO in templates/xmapper/dashboard.html
        While you're at it, it'd be nice to be able to upload new icons via web :)
    """
    COLOR_CHOICES = (
        ('AQ', 'aqua'),
        ('BK', 'black'),
        ('BL', 'blue'),
        ('FU', 'fuchsia'),
        ('GR', 'green'),
        ('GY', 'grey'),
        ('MN', 'maroon'),
        ('NV', 'navy'),
        ('OL', 'olive'),
        ('PU', 'purple'),
        ('RD', 'red'),
        ('SL', 'silver'),
        ('TL', 'teal'),
        ('WT', 'white'),
        ('YL', 'yellow'),
        ('RO', 'road'),
    )
    name = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='MN')

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
    print "** RECEIVED XFORM SIGNAL **"
    submission = args['submission']
    print submission
    xform = args['xform']
    print xform

    if not submission.has_errors:
        print "** NO XFORM ERRORS **"
        keyword = xform.keyword
        # assign to a Group according to XForm's keyword so all of an
        # XForm's submission markers are the same color
        group, created = Group.objects.get_or_create(name=xform.keyword)
        if created:
            print "** GROUP CREATED **"

        # make a nice little dict of {u'field.caption' : u'field.value'}s
        sub_vals = list(submission.values.all())
        print sub_vals
        captions = [s.field.caption for s in sub_vals]
        print captions
        values = [s.value for s in sub_vals]
        print values

        sub_dict = dict(zip(captions, values))
        print sub_dict

        # if XForm submission has a field captioned 'location', try to find 
        # a place that has a slug that matches the location field's value
        if "location" in sub_dict:
            print sub_dict["location"]
            place = Place.find_by_slug(sub_dict["location"]) 
            print place
            if place is not None:
                print "** FOUND PLACE **"
                print place
                #create XLoc
                xloc = XLoc.objects.create(submission=submission, place=place, group=group)
                print "** CREATED XLOC **"
                print xloc
            else:
                print "** COULD NOT FIND LOCATION **"

        # if XForm submission has fields captioned 'from' and 'to', try to find
        # places that have slugs that match these fields' values
        # and then create a new Place midway between these two places
        if "from" in sub_dict:
            print sub_dict["from"]
            if "to" in sub_dict:
                print sub_dict["to"]
                from_place = Place.find_by_slug(sub_dict["from"])
                print from_place
                to_place = Place.find_by_slug(sub_dict["to"])
                print to_place
                if from_place is not None:
                    print "** FOUND FROM **"
                    print from_place
                    if to_place is not None:
                        print "** FOUND TO **"
                        print to_place
                        mid_lat = (from_place.point.latitude + to_place.point.latitude)/D("2.0")
                        mid_lng = (from_place.point.longitude + to_place.point.longitude)/D("2.0")
                        midpoint = Point.objects.create(latitude=mid_lat, longitude=mid_lng)
                        print "** CREATED POINT **"
                        road_condition_place = Place.objects.create(name="road condition", slug="road-condition", point=midpoint)
                        print "** CREATED PLACE **"
                        xloc = XLoc.objects.create(submission=submission, place=road_condition_place, group=group)
                        print "** CREATED XLOC **"


# then wire it to the xform_received signal
xform_received.connect(handle_submission)
