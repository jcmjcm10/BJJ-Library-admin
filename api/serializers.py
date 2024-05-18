from rest_framework import serializers
from .models import Video, Tag, VideoTag, VideoList, VideoListItem
from users.models import User
from django.contrib.auth import get_user_model, authenticate
import json 

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

    def get_tags(self, videoPK=None):
        videoTags = VideoTag.objects.filter(video=videoPK)
        tagList = []
        for videoTag in videoTags:
            tagList.append(videoTag.tag.name)
      
        return tagList

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'tags': self.get_tags(instance.id),
            'title': instance.title,
            'url': instance.url,
            'youtubeID': instance.youtubeID,
        }

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class VideoTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoTag
        fields = '__all__'

class VideoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoList
        fields ='__all__'    
    
    def get_videos(self, instance):
        videoListItems = VideoListItem.objects.filter(videoList=instance.id).order_by('order')
        videoList = []
        for videoListItem in videoListItems:
            videoSerializer = VideoSerializer(videoListItem.video)
            videoList.append(videoSerializer.data)
        return videoList

    def to_representation(self, instance):
        videos = self.get_videos(instance)
        
        if instance.owner:
            user_name = instance.owner.username
        else:
            user_name = None

        return {
        'id': instance.id,
        'title': instance.title,
        'videos': videos,
        'owner': user_name
        }

