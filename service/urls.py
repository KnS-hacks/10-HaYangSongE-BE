from django.urls import path
from service import views

urlpatterns = [
    path('account/login', views.login),
    path('account/guest', views.GuestList.as_view()),
    path('account/guest/waiting/<str:username>', views.user_waiting),
    path('account/guest/<int:pk>', views.GuestDetailPK.as_view()),
    path('account/guest/<str:username>', views.GuestDetailUN.as_view()),
    path('account/restaurant', views.RestaurantList.as_view()),
    path('account/restaurant/create', views.get_restaurants),
    path('account/restaurant/<int:pk>', views.RestaurantDetail.as_view()),
    path('service/restaurant/waiting/<int:restaurant_pk>', views.accept_waiting),
    path('service/waiting', views.waiting),
    path('service/waiting/<int:pk>', views.WaitingDetail.as_view()),
]

