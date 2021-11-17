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
    full_name = serializers.CharField()
    password = serializers.CharField(write_only=True)
    friends = serializers.StringRelatedField(many=True)
    vaccine_elapsed = serializers.SerializerMethodField()
    is_host = serializers.BooleanField(read_only=True)

    @staticmethod
    def get_vaccine_elapsed(obj):
        if obj.vaccine_date:
            now = datetime.datetime.utcnow().replace(tzinfo=utc).date()
            diff = now - obj.vaccine_date
            return int(diff.total_seconds() // (60 * 60 * 24))


    class Meta:
        model = Guest
        fields = ['id', 'username', 'full_name', 'vaccine_step',
                  'vaccine_elapsed', 'email', 'vaccine_date',
                  'password', 'phone_number',
                  'is_staff', 'friends', 'is_host']


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


class RestaurantSerializer(serializers.ModelSerializer):
    waitings = 'WaitingSerializer(many=True, read_only=True)'
    acceptation = 'AcceptationSerializer(many=True, read_only=True)'
    SE = serializers.SerializerMethodField()
    WN = serializers.SerializerMethodField()

    def get_SE(self, obj):
        parent = child = 0
        restaurants = Restaurant.objects.filter(district='SE')
        for restaurant in restaurants:
            parent += restaurant.total_seat
            child += (restaurant.total_seat - restaurant.remain_seat)
        return 0 if not parent else int(child * 100 / parent)

    def get_WN(self, obj):
        parent = child = 0
        restaurants = Restaurant.objects.filter(district='WN')
        for restaurant in restaurants:
            parent += restaurant.total_seat
            child += (restaurant.total_seat - restaurant.remain_seat)
        return 0 if not parent else int(child * 100 / parent)


    class Meta:
        model = Restaurant
        fields = ['name', 'host', 'phone_number', 'branch_name', 'district', 'area',
                  'waiting_avg', 'total_seat', 'remain_seat', 'menu',
                  'waitings', 'acceptation', 'vaccine_condition', 'SE', 'WN']

    def create(self, validated_data):
        return Restaurant.objects.create(**validated_data)
