from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes

from account.models import Guest, Restaurant
from account.serializers import GuestSerializer, RestaurantSerializer


class GuestList(generics.ListCreateAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    permission_classes = []

    def perform_create(self, serializer):
        serializer.save()


class GuestDetail(generics.RetrieveUpdateAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'username'


class RestaurantList(generics.ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['phone_number', 'branch_name',
                     'district', 'area']

    def perform_create(self, serializer):
        serializer.save()


class RestaurantDetail(generics.RetrieveUpdateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]