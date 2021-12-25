from django.db import models
from django.contrib.auth.models import AbstractUser


class Guest(AbstractUser):
    full_name = models.CharField(max_length=32)
    vaccine_step = models.IntegerField(default=0)
    vaccine_date = models.DateField(null=True)
    phone_number = models.CharField(max_length=50, default="")
    is_host = models.BooleanField(default=False)
    waiting_record = models.ManyToManyField('Waiting', related_name='waiting_record',
                                            default=None, blank=True, null=True)
    waiting_current = models.ForeignKey('Waiting', on_delete=models.SET_NULL,
                                           related_name='waiting_current', default=None, blank=True, null=True)

    def __str__(self):
        return self.username


class Review(models.Model):
    score = models.FloatField()
    contents = models.TextField()


class Acceptation(models.Model):
    admission_date = models.DateTimeField(auto_now=True)
    waiting = models.ForeignKey('Waiting', on_delete=models.CASCADE)


class Restaurant(models.Model):
    DISTRICTS = [
        ('SE', '동남구'),
        ('WN', '서북구')
    ]
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
        ('27', '신당동'),
    ]

    # 가게 이름이 필요할 것 같아서 넣어봤어
    name = models.CharField(max_length=64)
    host = models.OneToOneField(Guest, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=64)
    branch_name = models.CharField(max_length=64)
    district = models.CharField(max_length=2, choices=DISTRICTS)
    area = models.CharField(max_length=2, choices=AREA)
    waiting_avg = models.IntegerField()
    menu = models.ImageField(upload_to=f'menu/%Y/%m/%d/', blank=True, null=True)
    restaurant_photo = models.ImageField(upload_to='restaurant/%Y/%m/%d/', blank=True)
    is_host = models.BooleanField(default=False)
    acceptation = models.ManyToManyField(Acceptation, blank=True)
    waitings = models.ManyToManyField('Waiting', related_name='waitings', blank=True)
    vaccine_condition = models.PositiveIntegerField(default=0)
    # density
    total_seat = models.IntegerField()
    remain_seat = models.IntegerField()

    def __str__(self):
        return self.name + " " + self.branch_name


class Waiting(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    leader = models.ForeignKey(Guest, on_delete=models.SET_NULL, null=True)
    member = models.ManyToManyField(Guest, related_name='member')
    accepted = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)
