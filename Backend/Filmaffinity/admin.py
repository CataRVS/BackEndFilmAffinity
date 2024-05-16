from django.contrib import admin
from .models import PlatformUsers, Movies, Actors, Directors, Categories, Rating

# Register your models here.
admin.site.register(PlatformUsers)
admin.site.register(Movies)
admin.site.register(Actors)
admin.site.register(Directors)
admin.site.register(Categories)
admin.site.register(Rating)
