from django.urls import path
from .views import add_product, create_product, delete_product, seller_products , seller_products_stats, update_product

urlpatterns = [
    path("product/add/<str:seller_id>/", add_product),
    path("product/stats/<str:seller_id>/", seller_products_stats),
    path("product/add/<str:seller_id>/", add_product),
    path("product/update/<str:product_id>/", update_product),
    path("product/delete/<str:product_id>/", delete_product),
]