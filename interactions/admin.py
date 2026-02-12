from django.contrib import admin

from .models import Favorite, Reaction, Subscription

admin.site.register(Reaction)
admin.site.register(Favorite)
admin.site.register(Subscription)
