import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
from service.models import Acceptation


class Guest(AbstractUser):
    vaccine_step = models.IntegerField(default=0)                                                       # 백신 접종 단계
    vaccine_date = models.DateField(null=True)                                                          # 백신 접종 일자
    phone_number = models.CharField(max_length=50, default="")                                          # 고객 휴대폰 번호
    friends = models.ManyToManyField("Guest", blank=True, related_name='friend_list')                   # 친구 목록
    friend_request_list = models.ManyToManyField("Guest", blank=True, related_name='friend_request')    # 친구 요청 목록

    def __str__(self):
        return self.username


class Restaurant(models.Model):
    host = models.OneToOneField(Guest, on_delete=models.CASCADE)                        # 점주 계정
    phone_number = models.CharField(max_length=50)                                      # 지점 전화 번호
    branch_name = models.CharField(max_length=50)                                       # 지점명
    district = models.CharField(max_length=50)                                          # 구
    area = models.CharField(max_length=50)                                              # 동
    waiting_avg = models.IntegerField()                                                 # 평균 대기 시간
    menu = models.ImageField(upload_to=f'menu/%Y/%m/%d', blank=True, null=True)         # 메뉴 사진
    restaurnat_photo = models.ImageField(upload_to=f'restaurant/%Y/%m/%d', blank=True)  # 식당 사진
    is_host = models.BooleanField(default=False)                                        # 호스트인지
    acceptation = models.ManyToManyField(Acceptation, blank=True)                       # 고객 입장 여부를 위해
    # density
    total_seat = models.IntegerField()                                                  # 수용 가능 인원
    remain_seat = models.IntegerField()                                                 # 입장 가능 인원

    def __str__(self):
        return self.branch_name + self.district
