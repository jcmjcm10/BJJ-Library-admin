from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import status



class Permission(object):    

    def dispatch(self, request, *args, **kwargs): 
        has_permission = True

        if has_permission:
            return super().dispatch(request, *args, **kwargs)
            
        response = Response({'error':'No tienes los permisos para la peticion'}, status=status.HTTP_403_FORBIDDEN)
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = 'application/json'
        response.renderer_context = {}
        return response   
        
