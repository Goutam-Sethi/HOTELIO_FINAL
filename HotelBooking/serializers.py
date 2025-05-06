from rest_framework import serializers

class PropertySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    location = serializers.CharField()
    license_number = serializers.CharField()
    price = serializers.FloatField()
    rooms_available = serializers.IntegerField()
    room_types = serializers.ListField(child=serializers.CharField())
    image_url = serializers.CharField(allow_null=True)
