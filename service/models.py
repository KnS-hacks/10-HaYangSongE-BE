from django.db import models
from django.contrib.auth.models import AbstractUser


class Guest(AbstractUser):
    full_name = models.CharField(max_length=32)
    vaccine_step = models.IntegerField(default=0)
    vaccine_date = models.DateField(null=True)
    phone_number = models.CharField(max_length=50, default="")
    is_host = models.BooleanField(default=False)
    waiting_record = models.ManyToManyField('Waiting', related_name='waiting_record',
                                            default=None, blank=True)
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


class Menu(models.Model):
    name = models.CharField(max_length=255)
    price = models.PositiveIntegerField()


class Restaurant(models.Model):
    DISTRICTS = [
        ('SE', '동남구'),
        ('WN', '서북구')
    ]

    # 가게 이름이 필요할 것 같아서 넣어봤어
    name = models.CharField(max_length=64)
    host = models.OneToOneField(Guest, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=64)
    branch_name = models.CharField(max_length=64)
    district = models.CharField(max_length=2, choices=DISTRICTS)
    detail_address = models.CharField(max_length=255)
    waiting_avg = models.IntegerField()
    menu = models.ManyToManyField(Menu)
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
