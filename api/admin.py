from django.contrib import admin

from .models import Video, Tag, VideoTag

# Register your models here.

@admin.register(Video)
class Video(admin.ModelAdmin):
    list_display = ('title',)

@admin.register(Tag)
class Tag(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(VideoTag)
class VideoTag(admin.ModelAdmin):
    list_display = ('video', 'tag')