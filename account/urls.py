from django.urls import path
from account import views

urlpatterns = [
    path('guest/', views.GuestList.as_view()),
    path('guest/<str:username>', views.GuestDetail.as_view()),
    path('restaurant/', views.RestaurantList.as_view()),
    path('restaurant/<int:pk>', views.RestaurantDetail.as_view()),
]