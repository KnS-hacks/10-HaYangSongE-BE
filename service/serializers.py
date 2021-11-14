from rest_framework import serializers

from service.models import Waiting, Acceptation


class WaitingSerializer(serializers.ModelSerializer):
    leader = serializers.StringRelatedField()
    # member = GuestSerializer(many=True)

    class Meta:
        model = Waiting
        fields = ['restaurant', 'leader', 'member']


class AcceptationSerializer(serializers.ModelSerializer):
    waiting = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = Acceptation
        fields = ['admission_date', 'waiting']
