from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, allow_blank=False, max_length=20)
    email = serializers.CharField(required=True, allow_blank=False, max_length=20)
    phone = serializers.IntegerField()

    def validate_phone(self, value):
        if not 1000000000 <= value < 9999999999:
            raise serializers.ValidationError("Phone number out of bounds")
        return value
