from django.shortcuts import render
import datetime
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils.timezone import utc

from account.models import Restaurant
from service.models import Waiting, Acceptation
from service.serializers import WaitingSerializer, AcceptationSerializer

from account.permissions import IsHostOrReadOnly


# Create your views here.
class WaitingList(generics.ListCreateAPIView):
    queryset = Waiting.objects.all()
    serializer_class = WaitingSerializer


class WaitingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Waiting.objects.all()
    serializer_class = WaitingSerializer


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated, IsHostOrReadOnly])
def accept_waiting(request, restaurant_pk):
    now = datetime.datetime.utcnow().replace(tzinfo=utc).date()
    if request.method == 'GET':
        acceptation = Acceptation.objects.filter(restaurant=restaurant_pk).filter(admission_date__day=now.day)
        serializer = AcceptationSerializer(acceptation, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        restaurant = Restaurant.objects.get(pk=restaurant_pk)
        waiting = Waiting.objects.filter(accepted=False).filter(date__day=now.day)\
            .order_by('-date')[0]
        acceptation = Acceptation.objects.create(
            waiting=waiting
        )
        restaurant.acceptation.add(acceptation)
        waiting.accepted = True
        serializer = AcceptationSerializer(data=acceptation)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
