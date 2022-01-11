import json
from datetime import datetime
from random import randrange

from django.core.management.base import BaseCommand, CommandError

from service.models import Guest, Restaurant, Menu


class Command(BaseCommand):
    help = 'Create mockup object'

    def handle(self, *args, **options):
        with open("mockup/service_restaurant.json", "r") as f:
            restaurants = json.load(f)
            rest_cnt = 1
            for restaurant in restaurants:
                user = Guest(
                    password=1234,
                    is_host=True,
                    email="1@1.com",
                    full_name=f'restaurant{rest_cnt}',
                    username=f'restaurants{rest_cnt}{datetime.today().isoformat()}',
                    vaccine_step=randrange(0, 3),
                )
                user.save()
                restaurant = Restaurant(
                    name=restaurant['name'],
                    host_id=user.id,
                    phone_number=restaurant['phone_number'],
                    branch_name="",
                    district=restaurant['district'],
                    detail_address=restaurant['detail_address'],
                    total_seat=randrange(20, 41),
                    remain_seat=randrange(10, 21),
                    waiting_avg=randrange(3, 11),
                    restaurant_photo=restaurant['restaurant_photo'],
                    vaccine_condition=randrange(0, 3)
                )
                restaurant.save()
                rest_cnt += 1
        with open("mockup/service_menu.json", "r") as f:
            menus = json.load(f)
            for menu_data in menus:
                menu = Menu(name=menu_data['name'],
                            price=menu_data['price'])
                menu.save()
        with open("mockup/service_restaurant_menu.json", "r") as rmf:
            restaurant_menu = json.load(rmf)
            restaurant = Restaurant.objects.get(id=1)
            for rm in restaurant_menu:
                if restaurant.id != rm['restaurant_id']:
                    restaurant = Restaurant.objects.get(id=rm['restaurant_id'])
                menu = Menu.objects.get(id=rm['menu_id'])
                restaurant.menu.add(menu)



