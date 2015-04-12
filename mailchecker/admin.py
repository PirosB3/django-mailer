from django.contrib import admin

from .models import Thread, Message
from .forms import MessageForm, MessageInlineForm


class MessageInline(admin.TabularInline):
    model = Message
    form = MessageInlineForm


class MessageAdmin(admin.ModelAdmin):
    ordering = ('id',)
    model = Message
    form = MessageForm


class ThreadAdmin(admin.ModelAdmin):
    inlines = [
        MessageInline,
    ]
    fields = ('number_of_messages',)
    list_display = ('id',)
    search_fields = ('to',)
    ordering = ('id',)


admin.site.register([Thread], ThreadAdmin)
admin.site.register([Message], MessageAdmin)
