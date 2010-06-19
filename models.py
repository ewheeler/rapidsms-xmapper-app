#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=5

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models
from xforms.models import XForm, XFormSubmission
from xforms.models import xform_received

class XLoc(models.Model):
    submission = models.ForeignKey(XFormSubmission)
    place = models.ForeignKey('Place')
    group = models.ForeignKey('Group', blank=True, null=True)

    def __unicode__(self):
        return "%s form from %s" % (self.submission.xform.keyword, self.place.name)

    @property
    def color(self):
        if self.group is not None:
            if self.group.color is not None:
                return self.group.get_color_display()
        return "red"

    @property
    def submitted_data(self):
        sub_vals = list(self.submission.values.all())
        captions = [str(s.field.caption) for s in sub_vals]
        values = [str(s.value) for s in sub_vals]

        sub_dict = dict(zip(captions, values))
        return sub_dict

    @property
    def submitted_data_for_web(self):
        sub_dict = self.submitted_data
        if "location" in sub_dict:
            location = sub_dict.pop("location")

        html = ""
        for key, value in sub_dict.items():
            item_html = "%s %s" % (str(value), str(key))
            html.append(item_html)

        return html

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
    name = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.name

class Group(models.Model):
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
        group, created = Group.objects.get_or_create(name=xform.keyword)
        if created:
            print "** GROUP CREATED **"

        sub_vals = list(submission.values.all())
        captions = [s.field.caption for s in sub_vals]
        values = [s.value for s in sub_vals]

        sub_dict = dict(zip(captions, values))

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


# then wire it to the xform_received signal
xform_received.connect(handle_submission)
