from django.contrib import admin
from .models import XLoc, Point, Place, Category

admin.site.register(XLoc)
admin.site.register(Point)
admin.site.register(Place)
admin.site.register(Category)
