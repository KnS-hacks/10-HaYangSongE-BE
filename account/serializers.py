import datetime
from django.db.models import fields

from django.utils.timezone import utc
from rest_framework import serializers
from account.models import Guest, Restaurant

class GuestSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    friends = serializers.StringRelatedField(many=True)
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
                  'password', 'photo', 'phone_number',
                  'is_staff', 'friends']


class RestaurantSerializer(serializers.ModelSerializer):
    host = serializers.StringRelatedField()


    class Meta:
        model = Restaurant
        fields = ['host', 'phone_number', 'branch_name', 'district', 'area',
                  'waiting_avg', 'total_seat', 'remain_seat', 'menu']