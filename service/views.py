from django.shortcuts import render
from rest_framework import generics
from service.models import Waiting
from service.serializers import WaitingSerializer


# Create your views here.
class WaitingList(generics.ListCreateAPIView):
    queryset = Waiting.objects.all()
    serializer_class = WaitingSerializer


class WaitingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Waiting.objects.all()
    serializer_class = WaitingSerializer

