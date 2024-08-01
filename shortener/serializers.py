from rest_framework import serializers

class GenerateURLSerializer(serializers.Serializer):
    long_url = serializers.URLField()
    custom_alias = serializers.CharField(required=False, allow_blank=True)
    ttl_seconds = serializers.IntegerField(required=False, default=120)

class UpdateURLSerializer(serializers.Serializer):
    custom_alias = serializers.CharField(required=False, allow_blank=True)
    ttl_seconds = serializers.IntegerField(required=False)
