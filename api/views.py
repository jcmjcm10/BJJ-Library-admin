from rest_framework import viewsets, mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.shortcuts import render
from .serializers import VideoSerializer, VideoTagSerializer, TagSerializer, VideoListSerializer
from .models import Video, Tag, VideoTag, VideoList
from users.authentication_mixins import Authentication
from users.permission_mixins import Permission

class VideoViewSet(Authentication, Permission, viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    authentication_classes = []
    http_method_names = ['get', 'post', 'put', 'delete']

    def create(self, request): 
        data = request.data
        videoData = {
            'title': data['title'],
            'url': data['url'],
            'youtubeID': data['youtubeID'],
        }
        video_serializer = self.serializer_class(data = videoData)
        # validation
        if video_serializer.is_valid():
            video_serializer.save()
            return Response(video_serializer.data, status=status.HTTP_200_OK)

        return Response(video_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def update(self, request, pk=None):
        video = Video.objects.filter(id = pk).first()
        data = request.data
        videoData = {
            'title': data['title'],
            'url': data['url'],
            'youtubeID': data['youtubeID'],
        }

        videos = VideoTag.objects.filter(video=pk)

        serializer_video = self.serializer_class(video, data=videoData)
        if serializer_video.is_valid():
            videos.delete()
            serializer_video.save()
            return Response(serializer_video.data, status=status.HTTP_200_OK)
        return Response(serializer_video.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):  
        video = Video.objects.filter(id=pk).first()
        if video:
            video.delete()
            return Response('Eliminación correcta',status=status.HTTP_200_OK)
        return Response('Video no encontrado',status=status.HTTP_400_BAD_REQUEST)

class TagViewSet(Authentication, viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    
    def get_queryset(self):        
        return  Tag.objects.all()

class VideoTagViewSet(Authentication, viewsets.ModelViewSet):
    queryset = VideoTag.objects.all()
    serializer_class = VideoTagSerializer
    
    def get_queryset(self):        
        return  VideoTag.objects.all()

    def create(self, request):
        data = request.data
        videoTagData = {
            'video': data['videoId'],
            'tag': data['tagId'],
        }

        serializer_videoTag = self.serializer_class(data=videoTagData)
        if serializer_videoTag.is_valid():
            serializer_videoTag.save()
            return Response(serializer_videoTag.data, status=status.HTTP_201_CREATED)

        return Response(serializer_videoTag.errors, status=status.HTTP_400_BAD_REQUEST)
       
class VideoListViewSet(Authentication, viewsets.ModelViewSet):
    queryset = VideoList.objects.all()
    serializer_class = VideoListSerializer
    