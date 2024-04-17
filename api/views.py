from rest_framework import viewsets, mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.shortcuts import render
from .serializers import VideoSerializer, VideoTagSerializer, TagSerializer
from .models import Video, Tag, VideoTag

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    authentication_classes = []
    permission_classes = [AllowAny]
    http_method_names = ['get', 'post', 'put', 'delete']

    def create(self, request):
        if request.headers['Authorization'] != 'smite2enprimavera':
            return Response('no tienes autirización para realizar la accion', status=status.HTTP_403_FORBIDDEN)
 
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
        if request.headers['Authorization'] != 'smite2enprimavera':
            return Response('no tienes autirización para realizar la accion', status=status.HTTP_403_FORBIDDEN)
        video = Video.objects.filter(id = pk).first()
        data = request.data
        videoData = {
            'title': data['title'],
            'url': data['url'],
            'youtubeID': data['youtubeID'],
        }

        videos = VideoTag.objects.filter(video=pk)
        videos.delete()

        serializer_video = self.serializer_class(video, data=videoData)
        if serializer_video.is_valid():
            serializer_video.save()
            return Response(serializer_video.data, status=status.HTTP_200_OK)
        return Response(serializer_video.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):  
        if request.headers['Authorization'] != 'smite2enprimavera':
            return Response('no tienes autirización para realizar la accion', status=status.HTTP_403_FORBIDDEN)
        video = Video.objects.filter(id=pk).first()
        if video:
            video.delete()
            return Response('Eliminación correcta',status=status.HTTP_200_OK)
        return Response('Video no encontrado',status=status.HTTP_400_BAD_REQUEST)

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    
    def get_queryset(self):        
        return  Tag.objects.all()

class VideoTagViewSet(viewsets.ModelViewSet):
    queryset = VideoTag.objects.all()
    serializer_class = VideoTagSerializer
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get_queryset(self):        
        return  VideoTag.objects.all()

    def create(self, request):
        if request.headers['Authorization'] != 'smite2enprimavera':
            return Response('no tienes autirización para realizar la accion', status=status.HTTP_403_FORBIDDEN)
        data = request.data
        videoTagData = {
            'video': data['videoId'],
            'tag': data['tagId'],
        }

        serializer_videoTag = self.serializer_class(data=videoTagData)
        if serializer_videoTag.is_valid():
            serializer_videoTag.save()
            return Response(serializer_videoTag.data, status=status.HTTP_201_CREATED)

        print(request.data)    

        return Response(serializer_videoTag.errors, status=status.HTTP_400_BAD_REQUEST)
       
