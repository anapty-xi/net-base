from rest_framework import serializers
from typing import List

class SerializerTableCreate(serializers.Serializer):
    table_title = serializers.CharField(max_length=32)
    cols = serializers.CharField()
    rows = serializers.CharField()

    @staticmethod
    def is_spec_sym(data):
        if False in list(map(lambda x: x not in list(".,:;!*-+()/#¤%&)"), data)):
            return True
        return False

    def validate_table_title(self, value):
        if SerializerTableCreate.is_spec_sym(value):
            raise serializers.ValidationError('Название не должно содержать специальный символы')
        return value

    def validate_cols(self, value):
        split_cols = value.split(';')
        for col in split_cols:
            if SerializerTableCreate.is_spec_sym(col):
                raise serializers.ValidationError('Название элемента таблицы не должно содержать специальные символы')
        return value

    def validate_rows(self, value):
        return self.validate_cols(value)
    

class SerializerQueryConditions(serializers.Serializer):
    conditions = serializers.JSONField()


class SerializerColUpdate(serializers.Serializer):
    row_pk = serializers.CharField()
    updates = serializers.JSONField()