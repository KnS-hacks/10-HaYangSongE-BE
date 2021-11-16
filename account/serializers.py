import datetime
from django.contrib.auth.models import update_last_login
from django.utils.timezone import utc
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from account.models import Guest, Restaurant

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


class GuestSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    vaccine_elapsed = serializers.SerializerMethodField()

    @staticmethod
    def get_vaccine_elapsed(obj):       # 백신 접종 경과 날짜 계산
        if obj.vaccine_date:
            now = datetime.datetime.utcnow().replace(tzinfo=utc).date()
            diff = now - obj.vaccine_date
            return int(diff.total_seconds() // (60 * 60 * 24))

    class Meta:
        model = Guest
        fields = ['username', 'vaccine_step',
                  'vaccine_elapsed', 'email',
                  'password', 'phone_number',
                  'is_staff']


class RestaurantSerializer(serializers.ModelSerializer):
    host = serializers.StringRelatedField()

    class Meta:
        model = Restaurant
        fields = ['host', 'phone_number', 'branch_name', 'district', 'area',
                  'waiting_avg', 'total_seat', 'remain_seat', 'menu']


class GuestLoginSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, attrs):
        username = attrs.get("username", None)
        password = attrs.get("password", None)
        guest = authenticate(username=username, password=password)

        if guest is None:
            return {
                'username': None
            }
        try:
            payload = JWT_PAYLOAD_HANDLER(guest)
            jwt_token = JWT_ENCODE_HANDLER(payload)
            update_last_login(None, guest)
        except Guest.DoesNotExist:
            raise serializers.ValidationError(
                '회원이 존재하지 않습니다.'
            )
        return {
            'username': guest.username,
            'token': jwt_token
        }


class MemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = Guest
        fields = ['username']
