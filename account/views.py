from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes

from account.models import Guest, Restaurant
from account.permissions import IsHostOrReadOnly
from account.serializers import GuestSerializer, RestaurantSerializer


class GuestList(generics.ListCreateAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    permission_classes = []

    def perform_create(self, serializer):
        serializer.save()


class GuestDetailUN(generics.RetrieveUpdateAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'username'


class GuestDetailPK(generics.RetrieveUpdateAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer


class RestaurantList(generics.ListCreateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated, IsHostOrReadOnly]

    def get_queryset(self):
        queryset = Restaurant.objects.all()
        district = self.request.query_params.get('district', None)
        key = self.request.query_params.get('key', None)
        if district is not None:
            queryset = queryset.filter(district=district)
        if key is not None:
            queryset = queryset.filter(branch_name__contains=key)
        return queryset


class RestaurantDetail(generics.RetrieveUpdateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated,
                          IsHostOrReadOnly]

