from rest_framework import serializers

class SereializerTableCreate(serializers.Serializer):
    table_title = serializers.CharField()
    cols = serializers.CharField()
    rows = serializers.CharField()

