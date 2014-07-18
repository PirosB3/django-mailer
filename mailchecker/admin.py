from django.contrib import admin
from .models import Thread, Message


class ThreadAdmin(admin.ModelAdmin):
    fields = ('number_of_messages',)
    list_display = ('id',)
    ordering = ('id',)


class MessageAdmin(admin.ModelAdmin):
    fields = ('sender', 'receiver', 'body')
    list_display = ('id',)
    ordering = ('id',)


admin.site.register([Message], MessageAdmin)
admin.site.register([Thread], ThreadAdmin)
