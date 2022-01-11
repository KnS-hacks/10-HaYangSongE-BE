import json
import os.path

import urllib.request
import re
from random import randrange

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotInteractableException, StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException

import requests

from django.utils.timezone import utc
from rest_framework import generics, permissions, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from django.http import JsonResponse

from service.permissions import IsHostOrReadOnly
from service.models import Guest, Restaurant, Waiting, Acceptation, Menu
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
        host = self.request.query_params.get('host', None)
        if district is not None:
            queryset = queryset.filter(district=district)
        if key is not None:
            queryset = queryset.filter(name__contains=key)
        if host is not None:
            queryset = queryset.filter(host_id=host)
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
@api_view(['GET', 'DELETE'])
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
        data["restaurant"] = str(restaurant.name)
        return Response(
            data,
            status=status.HTTP_200_OK
        )

    if request.method == 'DELETE':
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

            members = [waiting.leader]
            for member in waiting.member.all():
                members.append(member)
        except:
            data["msg"] = "멤버 조회 이슈"
            return Response(
                data,
                status=status.HTTP_200_OK
            )
        for member in members:
            member.waiting_current = None
        data["msg"] = f"waiting - {waiting.id} 가 성공적으로 삭제되었습니다."
        data["success"] = True
        waiting.restaurant = None
        waiting.leader = None
        waiting.accepted = False
        waiting.delete()

        return Response(
            data,
            status=status.HTTP_200_OK
        )


@api_view(["GET"])
def district_rate(request):
    def get_SE():
        parent = child = 0
        restaurants = Restaurant.objects.filter(district='SE')
        rate = 0
        for restaurant in restaurants:
            parent += restaurant.total_seat
            child += (restaurant.total_seat - restaurant.remain_seat)
        try:
            rate = int(child * 100 / parent)
            return rate
        except ZeroDivisionError:
            rate = 0
            return rate
        finally:
            return rate

    def get_WN():
        parent = child = 0
        restaurants = Restaurant.objects.filter(district='WN')
        rate = 0
        for restaurant in restaurants:
            parent += restaurant.total_seat
            child += (restaurant.total_seat - restaurant.remain_seat)
        try:
            rate = int(child * 100 / parent)
            return rate
        except ZeroDivisionError:
            rate = 0
            return rate
        finally:
            return rate

    if request.method == 'GET':
        data = {
            "SE": get_SE(),
            "WN": get_WN()
        }
        return Response(
            data,
            status=status.HTTP_200_OK
        )


@api_view(['POST'])
@permission_classes([IsAdminUser])
def get_restaurants(request):
    if request.method == 'POST':
        crawling()
        return Response({}, status=status.HTTP_200_OK)


def crawling():

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://map.kakao.com/")
    search_area = driver.find_element_by_css_selector('#search\.keyword\.query')
    search_area.send_keys("천안 식당")
    driver.find_element_by_css_selector('#search\.keyword\.submit').send_keys(Keys.ENTER)
    driver.implicitly_wait(3)
    more_page = driver.find_element_by_id("info.search.place.more")
    more_page.send_keys(Keys.ENTER)
    time.sleep(1)

    next_btn = driver.find_element_by_id("info.search.page.next")
    has_next = "disabled" not in next_btn.get_attribute("class").split(" ")
    current_page = 1
    rest_cnt = 1

    while has_next:
        time.sleep(1)
        page_links = driver.find_elements_by_css_selector("#info\.search\.page a")
        pages = [link for link in page_links if "HIDDEN" not in link.get_attribute("class").split(" ")]
        for i in range(1, 6):
            selector = f'#info\.search\.page\.no{i}'
            try:
                page = driver.find_element_by_css_selector(selector)
                page.send_keys(Keys.ENTER)
            except ElementNotInteractableException:
                break
            time.sleep(4)
            place_lists = driver.find_elements_by_css_selector('#info\.search\.place\.list > li')
            for p in place_lists:
                if rest_cnt > 100:
                    return rest_cnt
                try:
                    detail = p.find_element_by_css_selector('div.info_item > div.contact > a.moreview')
                except NoSuchElementException:
                    print("Promotion")
                    continue
                detail.send_keys(Keys.ENTER)
                driver.switch_to.window(driver.window_handles[-1])
                driver.implicitly_wait(3)

                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(3)
                try:
                    store = BeautifulSoup(driver.page_source, 'html.parser')
                except IndexError:
                    store = ""
                try:
                    name = store.select('.tit_location')[0].text
                except IndexError:
                    name = ""
                try:
                    address = store.select('.txt_address')[0].text
                except IndexError:
                    address = ""
                try:
                    tel = store.select('.txt_contact')[0].text
                except IndexError:
                    tel = ""
                try:
                    menus = store.select('.list_menu')[0].find_all("li")
                except:
                    menus = []
                district = 'SE' if address.split()[2] == '동남구' else 'WN'
                detail_address = ' '.join(address.split()[3:-1])

                user = Guest(
                    password=1234,
                    is_host=True,
                    email="1@1.com",
                    full_name=f'restaurant{rest_cnt}',
                    username=f'restaurants{rest_cnt}{datetime.datetime.today().isoformat()}',
                    vaccine_step=randrange(0, 3),
                )

                user.save()
                restaurant = Restaurant(
                    name=name,
                    host_id=user.id,
                    phone_number=tel,
                    branch_name="",
                    district=district,
                    detail_address=detail_address,
                    total_seat=randrange(20, 41),
                    remain_seat=randrange(10, 21),
                    waiting_avg=randrange(3, 11),
                    restaurant_photo=None,
                    vaccine_condition=randrange(0, 3)
                )
                restaurant.save()

                for idx, menu in enumerate(menus):
                    try:
                        menu_name = menu.select('.loss_word')[0].text
                    except Exception:
                        menu_name = ""
                    try:
                        menu_price = menu.select('.price_menu')[0].text
                        menu_price = int(''.join(menu_price.split()[1].split(',')))
                    except Exception:
                        menu_price = 0
                    menu = Menu(name=menu_name, price=menu_price)
                    menu.save()
                    restaurant.menu.add(menu)
                    print(menu_name, menu_price)

                place_photo_dir = f"restaurant/{restaurant.pk}/"
                place_photo = place_photo_dir + f"{restaurant.name}.jpeg"
                try:
                    photo_tag = driver.find_element_by_css_selector('span.bg_present')
                    photo_url = photo_tag.get_attribute('style')
                    photo_url_regex = re.search('"(.+?)"', photo_url)
                    if photo_url_regex:
                        photo_url_regex = photo_url_regex.group(1)
                    full_photo_url = parseURL(photo_url_regex)
                    if not os.path.isdir("media/" + place_photo_dir):
                        os.mkdir("media/" + place_photo_dir)
                    urllib.request.urlretrieve(full_photo_url, "media/" + place_photo)
                except Exception:
                    place_photo = None
                finally:
                    restaurant.restaurant_photo = place_photo
                    restaurant.save()

                print(place_photo)
                rest_cnt += 1
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        next_btn = driver.find_element_by_id("info.search.page.next")
        has_next = "disabled" not in next_btn.get_attribute("class").split(" ")
        if not has_next:
            driver.close()
            break
        else:
            current_page += 1
            next_btn.send_keys(Keys.ENTER)


def parseURL(url: str):
    replace = url.replace("%3F", "?")
    replace = replace.replace("%25", "%")
    return "http:" + replace
