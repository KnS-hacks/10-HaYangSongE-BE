import datetime

from django.contrib.auth.models import update_last_login
from django.utils.timezone import utc
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from service.models import Guest, Waiting, Restaurant, Acceptation, Menu
from django.contrib.auth import authenticate

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


class GuestSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField()
    password = serializers.CharField(write_only=True)
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
                  'is_staff', 'is_host', 'waiting_current']


class GuestLoginSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)
    success = serializers.BooleanField(default=False)

    def validate(self, attrs):
        username = attrs.get("username", None)
        password = attrs.get("password", None)
        guest = authenticate(username=username, password=password)
        if guest is None:
            guests = Guest.objects.filter(username=username)
            if not len(guests):
                guest = authenticate(username=username, password=password)
                return {
                    'username': None
                }
            guest = guests[0]
            if guest.password != password:
                return {
                    'username': None
                }
        try:
            jwt_token = self.get_user_token(guest)
            payload = JWT_PAYLOAD_HANDLER(guest)
            jwt_token = JWT_ENCODE_HANDLER(payload)
            update_last_login(None, guest)
        except Guest.DoesNotExist:
            return {
                'success': False,
                'username': 'UNKOWN',
                'token': ''
            }
        return {
            'success': True,
            'username': guest.username,
            'token': jwt_token
        }

    def get_user_token(self, guest):
        payload = JWT_PAYLOAD_HANDLER(guest)
        jwt_token = JWT_ENCODE_HANDLER(payload)
        update_last_login(None, guest)
        return jwt_token


class MemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = Guest
        fields = ['username']


class WaitingSerializer(serializers.ModelSerializer):
    leader = serializers.CharField()
    restaurant = 'RestaurantSerializer'
    order = serializers.SerializerMethodField()
    member = MemberSerializer(many=True)

    @staticmethod
    def get_order(obj):
        if obj.accepted:
            return 0
        now = datetime.datetime.utcnow().replace(tzinfo=utc).date()
        query = Waiting.objects.filter(date__lte=obj.date).filter(accepted=False)
        return len(query)

    class Meta:
        model = Waiting
        fields = ['id', 'restaurant', 'leader', 'member', 'accepted',
                  'date', 'order']


class AcceptationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acceptation
        fields = '__all__'


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'


class RestaurantSerializer(serializers.ModelSerializer):
    waitings = WaitingSerializer(many=True, read_only=True)
    acceptation = AcceptationSerializer(many=True, read_only=True)
    menu = MenuSerializer(many=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'host', 'phone_number', 'branch_name', 'district', 'detail_address',
                  'waiting_avg', 'total_seat', 'remain_seat', 'menu', 'restaurant_photo',
                  'waitings', 'acceptation', 'vaccine_condition']

    def create(self, validated_data):
        menu_data = validated_data.pop('menu')
        print(menu_data)
        restaurant = Restaurant.objects.create(**validated_data)
        for menu in menu_data:
            new_menu = Menu.objects.create(**menu)
            restaurant.menu.add(new_menu)
        return restaurant

