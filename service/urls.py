from django.urls import path
from service import views

urlpatterns = [
    path('district', views.district_rate),
    path('login', views.login),
    path('guest', views.GuestList.as_view()),
    path('guest/waiting/<str:username>', views.user_waiting),
    path('guest/<int:pk>', views.GuestDetailPK.as_view()),
    path('guest/<str:username>', views.GuestDetailUN.as_view()),
    path('restaurant', views.RestaurantList.as_view()),
    path('restaurant/create', views.get_restaurants),
    path('restaurant/<int:pk>', views.RestaurantDetail.as_view()),
    path('restaurant/waiting/<int:restaurant_pk>', views.accept_waiting),
    path('waiting', views.waiting),
    path('waiting/<int:pk>', views.WaitingDetail.as_view()),
]

