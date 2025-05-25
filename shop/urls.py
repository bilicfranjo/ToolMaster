from django.urls import path
from .views import (home_view, register_view, login_view, 
                    logout_view, diy_list_view, diy_detail_view, 
                    dashboard_home, admin_products_list, admin_product_create,
                    admin_product_edit, admin_product_delete, admin_diy_list,
                    admin_diy_create, admin_diy_edit, admin_diy_delete,
                    admin_banner_list, admin_banner_create, admin_banner_edit,
                    admin_banner_delete, admin_category_list, admin_category_create,
                    admin_category_edit, admin_category_delete, get_attributes_for_category)

urlpatterns = [
    path('', home_view, name="home"),
    path('register/', register_view, name="register"),
    path('login/', login_view, name="login"),
    path('logout/', logout_view, name='logout'),
    path('diy/', diy_list_view, name="diy_list"),
    path('diy/<int:pk>/', diy_detail_view, name="diy_detail"),
    path('dashboard/', dashboard_home, name='dashboard_home'),
    path('dashboard/proizvodi/', admin_products_list, name='admin_products_list'),
    path('dashboard/proizvodi/dodaj/', admin_product_create, name='admin_product_create'),
    path('dashboard/proizvodi/<int:pk>/uredi/', admin_product_edit, name='admin_product_edit'), # type: ignore
    path('dashboard/proizvodi/<int:pk>/obrisi/', admin_product_delete, name='admin_product_delete'),
    path('dashboard/diy/', admin_diy_list, name='admin_diy_list'),
    path('dashboard/diy/dodaj/', admin_diy_create, name='admin_diy_create'),
    path('dashboard/diy/<int:pk>/uredi/', admin_diy_edit, name='admin_diy_edit'),
    path('dashboard/diy/<int:pk>/obrisi/', admin_diy_delete, name='admin_diy_delete'),
    path('dashboard/banneri/', admin_banner_list, name='admin_banner_list'),
    path('dashboard/banneri/dodaj/', admin_banner_create, name='admin_banner_create'),
    path('dashboard/banneri/<int:pk>/uredi/', admin_banner_edit, name='admin_banner_edit'),
    path('dashboard/banneri/<int:pk>/obrisi/', admin_banner_delete, name='admin_banner_delete'),
    path('dashboard/kategorije/', admin_category_list, name='admin_category_list'),
    path('dashboard/kategorije/dodaj/', admin_category_create, name='admin_category_create'),
    path('dashboard/kategorije/<int:pk>/uredi/', admin_category_edit, name='admin_category_edit'),
    path('dashboard/kategorije/<int:pk>/obrisi/', admin_category_delete, name='admin_category_delete'),
    path('dashboard/api/atributi/<int:category_id>/', get_attributes_for_category, name='api_get_attributes'),
]

