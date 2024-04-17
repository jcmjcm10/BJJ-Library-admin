from rest_framework import serializers
from .models import Video, Tag, VideoTag
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


        

        
