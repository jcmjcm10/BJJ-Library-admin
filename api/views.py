from django.db.models import Q
from rest_framework import viewsets, mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.shortcuts import render
from .serializers import VideoSerializer, VideoTagSerializer, TagSerializer, VideoListSerializer
from .models import Video, Tag, VideoTag, VideoList, VideoListItem
from users.authentication_mixins import Authentication
from users.permission_mixins import Permission

def getLastOrderPlayList(videoListId):
    videolistItems = VideoListItem.objects.filter(videoList = videoListId)
    lastOrder = videolistItems.order_by('-order').first()
    if lastOrder:
        return lastOrder.order
    else:
        return 0

class VideoViewSet(Authentication, Permission, viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    authentication_classes = []
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset (self): 
        return Video.objects.filter(Q(owner=self.user) | Q(visibility='public'))

    def create(self, request): 
        data = request.data 
        data['owner'] = self.user.id
        video_serializer = self.serializer_class(data = data)        
        
        # validation
        if video_serializer.is_valid():
            video = video_serializer.save()

            #Insert video in List
            if 'list' in data and data['list'] is not None:
                list = VideoList.objects.filter(id=data['list']).first()
                if list is None: 
                    video.delete()
                    return Response({'message': 'No se a encontrado la lista de videos a la cual se quiere inserir.'},status=status.HTTP_400_BAD_REQUEST)

                if list.owner != self.user:
                    video.delete()
                    return Response({'message': 'No tienes permisos para publicar un video en esta Lista.'},status=status.HTTP_403_FORBIDDEN)

                getLastOrderPlayList(list.id)
                videoListItem = VideoListItem.objects.create(
                    videoList = list,
                    video = video,
                    order = getLastOrderPlayList(list.id) + 1,
                )
                videoListItem.save()
                list.save()

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

            if not video.owner == self.user and not self.user.is_staff:
                return Response('No tienes permisos para eliminar este video.',status=status.HTTP_403_FORBIDDEN)
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
    serializer_class = VideoListSerializer
    queryset = VideoList.objects.all()

    def get_queryset (self): 
        return VideoList.objects.filter(Q(owner=None) | Q(owner=self.user))

    # def list (self, request): 
    #     qs = VideoList.objects.filter(Q(owner=None) | Q(owner=self.user))
    #     videoListSerializer = VideoListSerializer(data=qs, many=True)
    #     videoListSerializer.is_valid()
    #     for videoList in  videoListSerializer.data:
    #         print(videoList)
    #     return Response(videoListSerializer.data, status=status.HTTP_200_OK)

    def create(self, request): 
        data = request.data
        data['owner'] = self.user.id
        videolistSerializer = self.serializer_class(data=data)
        if videolistSerializer.is_valid():
            videolistSerializer.save()
            return Response(videolistSerializer.data,status=status.HTTP_201_CREATED)

        return Response(videolistSerializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):  
        videoList = VideoList.objects.filter(id=pk).first()
        if videoList:
            if not videoList.owner == self.user:
                return Response('No tienes permisos para eliminar esta lista.',status=status.HTTP_403_FORBIDDEN)
            videoList.delete()
            return Response('Eliminación correcta',status=status.HTTP_200_OK)
        return Response('Lista no encontrado',status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        #Insert video in List    
        data = request.data
        if not 'op' in data:
            return Response({'message': 'No se ha especificado el tipo de operación'}, status=status.HTTP_400_BAD_REQUEST)

        if 'video' in data:
            video_list = VideoList.objects.filter(id=pk).first()
            if video_list is None: 
                return Response({'message': 'No se a encontrado la lista de videos a la cual se quiere inserir.'},status=status.HTTP_400_BAD_REQUEST)
           
            if data['op'] == 'insert':           
                if video_list.owner != self.user:
                    return Response({'message': 'No tienes permisos para publicar un video en esta Lista.'},status=status.HTTP_403_FORBIDDEN)

                video = Video.objects.filter(id=data['video']).first()
                if video:
                    videoListItem = VideoListItem.objects.create(
                        videoList = video_list,
                        video = video,
                        order = getLastOrderPlayList(video_list.id) + 1,
                    )
                    videoListItem.save()
                    videoListSerializer = VideoListSerializer(video_list)
                    return Response(videoListSerializer.data, status=status.HTTP_200_OK)
                
            elif data['op'] == 'remove':
                if video_list:
                    video_list.videos.remove(data['video'])
                    video_list.save()
                    
                    # Reorder
                    videoListItems = VideoListItem.objects.filter(videoList = video_list).order_by('order')

                    orderValue = 1
                    for item in videoListItems:
                        item.order = orderValue
                        item.save()
                        orderValue += 1

                    return Response({'message': 'El video se a eliminado de la lista correctamente.'}, status=status.HTTP_200_OK) 

            elif data['op'] == 'up':
                videoListItem = VideoListItem.objects.filter(videoList=pk).order_by('order')
                print(videoListItem)
                for videoItem in videoListItem:
                    if videoItem.video.id == data['video']:
                        if videoItem_ant is None:
                            return Response({'message': 'El vido ya se encuentra en la primera posicion'}, status=status.HTTP_400_BAD_REQUEST)
                        aux_order = videoItem.order
                        videoItem.order = videoItem_ant.order
                        videoItem_ant.order = aux_order
                        videoItem.save()
                        videoItem_ant.save()
                        print('se izo esto up')
                        break
                    videoItem_ant = videoItem
                return Response({'message': 'Operacion realizada con exito'}, status=status.HTTP_200_OK)
            elif data['op'] == 'down':
                videoListItem = VideoListItem.objects.filter(videoList=pk).order_by('order')
                print(videoListItem)
                videoItem_ant = None
                for videoItem in videoListItem:
                    if videoItem_ant is not None and videoItem_ant.video.id == data['video']:
                        aux_order = videoItem.order
                        videoItem.order = videoItem_ant.order
                        videoItem_ant.order = aux_order
                        videoItem.save()
                        videoItem_ant.save()
                        print('se izo esto down')
                        break
                    videoItem_ant = videoItem
                return Response({'message': 'Operacion realizada con exito'}, status=status.HTTP_200_OK)
        return Response({'message': 'Error, petición invalida.'}, status=status.HTTP_400_BAD_REQUEST)
