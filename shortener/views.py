from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from shortener import memory_storage
from .serializers import GenerateURLSerializer, UpdateURLSerializer
from django.shortcuts import redirect, render

class GenerateShortenedURLView(APIView):
    def post(self, request):
        
        serializer = GenerateURLSerializer(data=request.data)
        if serializer.is_valid():
            original_url = serializer.validated_data['long_url']
            custom_alias = serializer.validated_data.get('custom_alias')
            ttl = serializer.validated_data.get('ttl_seconds', 120)

           
            random_alias = True if not custom_alias else False
            with memory_storage.lock:

                alias = ""
                
                if not random_alias:
                    temp =memory_storage.url_mapping.get(custom_alias)
                    if temp:
                        return Response({'error': 'Alias already exists'}, status=status.HTTP_400_BAD_REQUEST)
                    alias = custom_alias
                else:
                    alias = memory_storage.generate_random_alias()
                    while alias in memory_storage.url_mapping:
                        alias = memory_storage.generate_random_alias()
                

                memory_storage.url_mapping[alias] = original_url
                memory_storage.ttl_info[alias] = datetime.now() + timedelta(seconds=ttl)
                memory_storage.access_logs[alias] = []
            
            return Response({'short_url': f'{request.scheme}://{request.META["HTTP_HOST"]}/{alias}'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RedirectView(APIView):
    def get(self, request, alias):
        with memory_storage.lock:
            if alias in memory_storage.url_mapping and memory_storage.ttl_info[alias] > datetime.now():
                memory_storage.access_logs[alias] = memory_storage.access_logs[alias]=memory_storage.access_logs[alias]+[datetime.now()]
                return redirect(memory_storage.url_mapping[alias])
            else:
                return Response({'error': 'URL expired or not found'}, status=status.HTTP_404_NOT_FOUND)

class AnalyticsView(APIView):
    def get(self, request, alias):
        with memory_storage.lock:
            if alias in memory_storage.url_mapping :
                access_times = memory_storage.access_logs.get(alias, [])
                return Response({
                    'long_url': memory_storage.url_mapping[alias],
                    'alias': alias,
                    'access_count': len(access_times),
                    'access_times': access_times[-10:]
                })
            else:
                return Response({'error': 'Alias not found'}, status=status.HTTP_404_NOT_FOUND)

class UpdateShortenedURLView(APIView):
    def put(self, request, alias):
        serializer = UpdateURLSerializer(data=request.data)
        
        if serializer.is_valid():
            new_alias = serializer.validated_data.get('custom_alias')
            ttl = serializer.validated_data.get('ttl_seconds')

            with memory_storage.lock:
                if alias in memory_storage.url_mapping :
                    original_url = memory_storage.url_mapping[alias]
                    if new_alias:
                        del memory_storage.url_mapping[alias]
                        memory_storage.url_mapping[new_alias] = original_url
                        memory_storage.ttl_info[new_alias] = memory_storage.ttl_info.pop(alias)
                        memory_storage.access_logs[new_alias] = memory_storage.access_logs.pop(alias, [])
                    if ttl:
                        memory_storage.ttl_info[new_alias or alias] = datetime.now() + timedelta(seconds=int(ttl))
                    return Response({'short_url': f'{request.scheme}://{request.META["HTTP_HOST"]}/{new_alias}'})
                else:
                    return Response({'error': 'Alias  not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteShortenedURLView(APIView):
    def delete(self, request, alias):
        with memory_storage.lock:
            exists = memory_storage.url_mapping.get(alias)
            if exists :
                del memory_storage.url_mapping[alias]
                del memory_storage.ttl_info[alias]
                del memory_storage.access_logs[alias]
                return Response({'message': 'deleted successfully'})
            else:
                return Response({'error': 'Alias not found'}, status=status.HTTP_404_NOT_FOUND)
