from django.db import models
from django.contrib.auth.models import AbstractUser
from service.models import Acceptation


class Guest(AbstractUser):
    name = models.CharField(max_length=32)                                                              # 이름
    vaccine_step = models.IntegerField(default=0)                                                       # 백신 접종 단계
    vaccine_date = models.DateField(null=True)                                                          # 백신 접종 일자
    phone_number = models.CharField(max_length=64, default="")                                          # 고객 휴대폰 번호
    friends = models.ManyToManyField("Guest", blank=True, related_name='friend_list')                   # 친구 목록 (시간이 남는다면 구현)
    friend_request_list = models.ManyToManyField("Guest", blank=True, related_name='friend_request')    # 친구 요청 목록 (시간이 남는다면 구현)

    def __str__(self):
        return self.username


class Restaurant(models.Model):
    DISTRICTS = [
        ('SE', '동남구'),
        ('WN', '서북구')]
    AREA = [
        ('01', '목천읍'),
        ('02', '풍세면'),
        ('03', '광덕면'),
        ('04', '북면'),
        ('05', '성남면'),
        ('06', '수신면'),
        ('07', '병천면'),
        ('08', '동면'),
        ('09', '중앙동'),
        ('10', '문성동'),
        ('11', '원성1동'),
        ('12', '원성2동'),
        ('13', '신안동'),
        ('14', '봉명동'),
        ('15', '일봉동'),
        ('16', '신방동'),
        ('17', '청룡동'),
        ('18', '성환읍'),
        ('19', '직산읍'),
        ('20', '성거읍'),
        ('21', '입장면'),
        ('22', '성정동'),
        ('23', '불당동'),
        ('24', '백석동'),
        ('25', '두정동'),
        ('26', '부대동'),
        ('27', '신당동')]

    name = models.CharField(max_length=64)                                              # 매장 이름
    host = models.OneToOneField(Guest, on_delete=models.CASCADE)                        # 점주 계정
    phone_number = models.CharField(max_length=64)                                      # 지점 전화 번호
    branch_name = models.CharField(max_length=64)                                       # 지점명
    district = models.CharField(max_length=2, choices=DISTRICTS)                        # 구
    area = models.CharField(max_length=2, choices=AREA)                                 # 동
    waiting_avg = models.PositiveIntegerField()                                         # 평균 대기 시간
    menu = models.ImageField(upload_to=f'menu/%Y/%m/%d', blank=True, null=True)         # 메뉴 사진
    restaurant_photo = models.ImageField(upload_to=f'restaurant/%Y/%m/%d', blank=True)  # 식당 사진
    is_host = models.BooleanField(default=False)                                        # 호스트인지
    acceptation = models.ManyToManyField(Acceptation, blank=True)                       # 고객 입장 여부를 위해
    waitings = models.ManyToManyField('service.Waiting', related_name='waitings', blank=True)   # 관련 웨이팅들
    vaccine_condition = models.PositiveIntegerField(default=0)
    # density
    total_seat = models.IntegerField()                                                  # 수용 가능 인원
    remain_seat = models.IntegerField()                                                 # 입장 가능 인원

    def __str__(self):
        return self.branch_name + self.district
