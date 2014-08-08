from django.contrib import admin
from .models import Post, Comment


class CommentInline(admin.TabularInline):
    model = Comment


class PostAdmin(admin.ModelAdmin):
    inlines = [
        CommentInline,
    ]
    fields = ('title',)
    list_display = ('id',)
    ordering = ('id',)


#class MessageAdmin(admin.ModelAdmin):
    #fields = ('sender', 'receiver', 'body')
    #list_display = ('id',)
    #ordering = ('id',)


admin.site.register([Post], PostAdmin)
#admin.site.register([Thread], ThreadAdmin)
# Register your models here.
