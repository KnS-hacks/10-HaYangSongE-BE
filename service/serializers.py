from rest_framework import serializers

from service.models import Waiting, Acceptation
from account.models import Guest


class WaitingSerializer(serializers.ModelSerializer):
    leader = serializers.CharField()
    restaurant = 'RestaurantSerializer'
    order = serializers.SerializerMethodField()
    member = 'MemberSerializer(many=True)'

    def create(self, validated_data):
        restaurant_ = validated_data.pop('restaurant')
        leader_ = validated_data.pop('leader')
        leader = Guest.objects.get(username=leader_)
        members = validated_data.pop('member')
        waiting = Waiting.objects.create(**validated_data,
                                         leader_id=leader.pk,
                                         restaurant_id=restaurant_.pk)
        if leader.vaccine_step < restaurant_.vaccine_condition:
            raise serializers.ValidationError(
                {"message": "백신 조건이 맞지않습니다."}
            )
        try:
            for member_ in members:
                member = Guest.objects.get(username=member_['username'])
                if member.vaccine_step < restaurant_.vaccine_condition:
                    raise serializers.ValidationError(
                        {"message": "백신 조건이 맞지않습니다."}
                    )
                waiting.member.add(member)
        except Guest.DoesNotExist:
            raise serializers.ValidationError(
                {"message": '회원이 존재하지 않습니다.'}
            )
        restaurant_.waitings.add(waiting)
        return waiting

    @staticmethod
    def get_order(obj):
        if obj.accepted:
            return 0
        query = Waiting.objects.filter(date__lte=obj.date).\
            filter(accepted=False)
        return len(query)

    class Meta:
        model = Waiting
        fields = ['id', 'restaurant', 'leader', 'member', 'accepted',
                  'date', 'order']


class AcceptationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acceptation
        fields = '__all__'

