from rest_framework import serializers

from service.models import Waiting, Acceptation
from account.serializers import GuestSerializer


class WaitingSerializer(serializers.ModelSerializer):
    leader = serializers.StringRelatedField()
    member = GuestSerializer(many=True)

    class Meta:
        model = Waiting
        fields = ['restaurant', 'leader', 'member']


class AcceptationSerializer(serializers.ModelSerializer):
    waiting = serializers.PrimaryKeyRelatedField(many=True,
                                                 queryset=Waiting.objects.all())

    class Meta:
        model = Acceptation
        fields = ['admission_date', 'waiting']
