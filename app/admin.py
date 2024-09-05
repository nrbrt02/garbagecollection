from django.contrib import admin
from app.models import Location, User, Residence, Client, Schedule, Collection, Overflow, Feedback
# Register your models here.
admin.site.register(Location)
admin.site.register(User)
admin.site.register(Residence)
admin.site.register(Client)
admin.site.register(Schedule)
admin.site.register(Collection)
admin.site.register(Overflow)
admin.site.register(Feedback)