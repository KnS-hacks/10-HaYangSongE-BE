from django.urls import path
from account import views

urlpatterns = [
    path('login/', views.login),
    path('guest/', views.GuestList.as_view()),
    path('guest/<int:pk>', views.GuestDetailPK.as_view()),
    path('guest/<str:username>', views.GuestDetailUN.as_view()),
    path('restaurant/', views.RestaurantList.as_view()),
    path('restaurant/<int:pk>', views.RestaurantDetail.as_view()),
]