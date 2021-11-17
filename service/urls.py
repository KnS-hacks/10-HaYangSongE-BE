from django.urls import path
from service import views

urlpatterns = [
    path('waiting/', views.WaitingList.as_view()),
    path('waiting/<int:pk>/', views.WaitingDetail.as_view()),
    path('restaurant/waiting/<int:restaurant_pk>/', views.accept_waiting),
]
