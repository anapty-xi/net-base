from rest_framework import serializers

class SereializerTableCreate(serializers.Serializer):
    cols = serializers.CharField()
    rows = serializers.CharField()

