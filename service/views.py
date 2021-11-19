import datetime

import requests

from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import JsonResponse

# from service.permissions import IsHostOrReadOnly
from service.models import Guest, Restaurant, Waiting, Acceptation
from service.serializers import GuestSerializer, RestaurantSerializer, WaitingSerializer
from service.serializers import AcceptationSerializer, GuestLoginSerializer
from django.views.decorators.csrf import csrf_exempt

from rest_framework.parsers import JSONParser


class GuestList(generics.ListCreateAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    filter_backends = [filters.SearchFilter]
    # permission_classes = []
    search_fields = ['username']

    def perform_create(self, serializer):
        serializer.save()


class GuestDetailUN(generics.RetrieveUpdateAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'username'


class GuestDetailPK(generics.RetrieveUpdateAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer


class RestaurantList(generics.ListCreateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    # permission_classes = [permissions.IsAuthenticated, IsHostOrReadOnly]

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


class WaitingList(generics.ListCreateAPIView):
    queryset = Waiting.objects.all()
    serializer_class = WaitingSerializer
    # permission_classes = [permissions.IsAuthenticated]


class WaitingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Waiting.objects.all()
    serializer_class = WaitingSerializer
    # permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@csrf_exempt
def login(request):
    if request.method == 'POST':
        serializer = GuestLoginSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            response = {
                'success': False,
            }
            return Response(response, status=status.HTTP_200_OK)
        response = {
            'success': True,
            'username': serializer.data['username'],
            'token': serializer.data['token']
        }
        return Response(response, status=status.HTTP_200_OK)


# @permission_classes([permissions.IsAuthenticated, IsHostOrReadOnly])
@csrf_exempt
@api_view(['GET', 'POST'])
def accept_waiting(request, restaurant_pk):
    if request.method == 'GET':
        acceptation = Acceptation.objects.filter(restaurant=restaurant_pk)
        serializer = AcceptationSerializer(acceptation, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        restaurant = Restaurant.objects.get(pk=restaurant_pk)
        waiting = Waiting.objects.filter(restaurant_id=restaurant_pk)\
            .filter(accepted=False)\
            .order_by('date')[0]
        acceptation = Acceptation.objects.create(
            waiting=waiting
        )
        restaurant.acceptation.add(acceptation)
        waiting.accepted = True
        waiting.save()
        serializer = AcceptationSerializer(data=acceptation)
        if serializer.is_valid():
            serializer.save()
        return Response(
            {
                "success": True
            }, status=status.HTTP_201_CREATED
        )


@csrf_exempt
@api_view(['GET', 'POST'])
def waiting(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        waiting = Waiting()
        restaurant_ = data['restaurant']
        leader_ = data['leader']
        members_ = data['member']
        restaurant = Restaurant.objects.get(id=restaurant_)
        leader = Guest.objects.get(username=leader_)

        if leader.vaccine_step < restaurant.vaccine_condition:
            return Response({
                "success": False,
                "msg": "백신 조건이 맞지않습니다."
            })

        waiting.restaurant_id = restaurant_
        waiting.restaurant = restaurant
        waiting.leader = leader
        waiting.leader_id = leader_
        waiting.accepted = False
        waiting.date = datetime.datetime.utcnow()
        try:
            for member_ in members_:
                member = Guest.objects.get(username=member_['username'])
                if member.vaccine_step < restaurant.vaccine_condition:
                    return Response({
                        "success": False,
                        "msg": "백신 조건이 맞지않습니다."
                    }, status=status.HTTP_400_BAD_REQUEST)
                waiting.member.add(member)
            waiting.save()
        except Guest.DoesNotExist:
            return Response({
                "success": False,
                "msg": "멤버 이름이 존재하지 않습니다."
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            data,
            status=status.HTTP_201_CREATED
        )
    elif request.method == 'GET':
        waitings = Waiting.objects.all()
        serilaizer = WaitingSerializer(waitings, many=True)
        return JsonResponse(serilaizer.data, safe=False)
