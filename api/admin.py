from django.contrib import admin

from .models import Video, Tag, VideoTag, VideoList, VideoListItem

# Register your models here.

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'visibility')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(VideoTag)
class VideoTagAdmin(admin.ModelAdmin):
    list_display = ('video', 'tag')


class VideoListItemAdminInLine(admin.TabularInline):
    model = VideoListItem
    extra = 0
    fields = ('video','show_tags','order')
    readonly_fields = ('show_tags',)

@admin.register(VideoList)
class VideoListAdmin(admin.ModelAdmin):
    inlines = [
        VideoListItemAdminInLine,
    ]
    