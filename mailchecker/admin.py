from django.contrib import admin
from .models import Thread


class ThreadAdmin(admin.ModelAdmin):
    fields = ('number_of_messages',)
    list_display = ('id',)
    ordering = ('id',)

admin.site.register([Thread], ThreadAdmin)
