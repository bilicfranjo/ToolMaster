from django.urls import path
from .views import home_view, register_view, login_view, logout_view, diy_list_view, diy_detail_view

urlpatterns = [
    path('', home_view, name="home"),
    path('register/', register_view, name="register"),
    path('login/', login_view, name="login"),
    path('logout/', logout_view, name='logout'),
    path('diy/', diy_list_view, name="diy_list"),
    path('diy/<int:pk>/', diy_detail_view, name="diy_detail"),
]

