import datetime
import json
import sys
import os.path

import requests

from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django.utils.timezone import utc
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

from service.sms.lib.auth import *
from service.sms.lib.config import *


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
        if serializer.data['success']:
            response = {
                'success': serializer.data['success'],
                'username': serializer.data['username'],
                'token': serializer.data['token']
            }
        else:
            response = {
                'success': serializer.data['success'],
                'username': '',
                'token': ''
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
        try:
            waiting = Waiting.objects.filter(restaurant_id=restaurant_pk)\
                .filter(accepted=False)\
                .order_by('date')[0]
            acceptation = Acceptation.objects.create(
                waiting=waiting
            )
        except:
            return Response(
                {
                    "success": False,
                    "msg": "대기중인 인원이 없습니다"
                }
            )
        restaurant.acceptation.add(acceptation)
        waiting.accepted = True
        waiting.save()
        members = []

        for guest in waiting.member.all():
            members.append(guest)
        members.append(waiting.leader)
        for guest in members:
            guest.waiting_current.save()
            guest.waiting_record.add(guest.waiting_current)
            guest.waiting_current = None
            guest.save()

        try:
            next_waiting = Waiting.objects.filter(restaurant_id=restaurant_pk)\
                    .filter(accepted=False)\
                    .order_by('date')[0]
            leader = Guest.objects.get(username=next_waiting.leader.username)
            sms = {
                    'message': {
                        'to': leader.phone_number,
                        'from': '#',
                        'text': f'안녕하세요. VAC STAGE입니다. \
                        {next_waiting.leader} 님이 예약하신 "{restaurant}" 대기 순서 문자 보내드립니다. {restaurant.waiting_avg}분 뒤 입장 예정이오니, 음식점 앞에 대기 부탁드립니다. 감사합니다!'
                    }
                }
            res = requests.post(getUrl('/messages/v4/send'),
                                headers=get_headers(apiKey, apiSecret), json=sms)
            print(json.dumps(json.loads(res.text), indent=2, ensure_ascii=False))
        except:
            return Response(
                {
                    "success": True,
                    "msg": "다음 예약은 없습니다."
                }, status=status.HTTP_200_OK
            )
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
        members = []

        try:
            for member_ in members_:
                members.append(Guest.objects.get(username=member_['username']))
            members.append(leader)
        except Guest.DoesNotExist:
            return Response({
                "success": False,
                "msg": "멤버 이름이 존재하지 않습니다."
            }, status=status.HTTP_400_BAD_REQUEST)

        for member in members:
            if member.vaccine_step < restaurant.vaccine_condition:
                return Response({
                    "success": False,
                    "msg": "백신 조건이 맞지않습니다."
                })
            if member.waiting_current is not None:
                return Response({
                    "success": False,
                    "msg": f"{member.username}이 이미 예약 목록을 가지고 있습니다."
                }, status=status.HTTP_400_BAD_REQUEST)

        waiting.restaurant_id = restaurant_
        waiting.restaurant = restaurant
        waiting.leader = leader
        waiting.accepted = False
        waiting.date = datetime.datetime.utcnow()
        waiting.save()
        for member in members:
            waiting.member.add(member.id)
            member.waiting_current = waiting
            member.save()
        waiting.save()

        now = datetime.datetime.utcnow().replace(tzinfo=utc).date()
        query = Waiting.objects.filter(date__lte=waiting.date).filter(accepted=False)
        data['order'] = len(query)
        data['time'] = len(query) * restaurant.waiting_avg

        return Response(
            data,
            status=status.HTTP_201_CREATED
        )
    elif request.method == 'GET':
        waitings = Waiting.objects.all()
        serilaizer = WaitingSerializer(waitings, many=True)
        return JsonResponse(serilaizer.data, safe=False)


@csrf_exempt
@api_view(['GET'])
def user_waiting(request, username):
    if request.method == 'GET':
        data = {
            "success": False
        }
        try:
            guest: Guest = Guest.objects.get(username=username)
        except Guest.DoesNotExist:
            data["msg"] = "존재하지 않는 사용자입니다."
            return Response(
                data,
                status=status.HTTP_200_OK
            )
        try:
            waiting: Waiting = guest.waiting_current
            now = datetime.datetime.utcnow().replace(tzinfo=utc).date()
            query = Waiting.objects.filter(date__lte=waiting.date).filter(accepted=False)

            order = len(query)
            members = [str(waiting.leader)]
            for member in waiting.member.all():
                members.append(str(member.username))
        except:
            data["msg"] = "멤버 조회 이슈"
            return Response(
                data,
                status=status.HTTP_200_OK
            )
        try:
            pk = waiting.restaurant.pk
            restaurant_ = waiting.restaurant.name
            restaurant = Restaurant.objects.get(pk=pk)
        except:
            data["msg"] = "식당 조회 이슈"
            return Response(
                data,
                status=status.HTTP_200_OK
            )
        data["success"] = True
        data["members"] = members
        data["order"] = order
        data["left_time"] = int(restaurant.waiting_avg * order)
        data["restaurant"] = str(restaurant)
        return Response(
            data,
            status=status.HTTP_200_OK
        )
