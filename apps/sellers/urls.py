from django.urls import path
from apps.sellers.views import seller_dashboard, seller_login, seller_bank_details, seller_transactions
from apps.sellers.views import seller_onboarding , seller_register
from .views import seller_kyc_status, seller_order_details, seller_orders, seller_orders_stats, update_order_status, upload_kyc_document
urlpatterns = [

    path("register/", seller_register, name="seller_register"),
    path("info/", seller_onboarding, name="seller_onboarding"),
    path("login/", seller_login, name="seller_login"),
    path("api/seller/dashboard/<str:seller_id>/", seller_dashboard),
    path("api/seller/bank-details/<str:seller_id>/", seller_bank_details),
    path("api/seller/transactions/<str:seller_id>/", seller_transactions),
    path("api/seller/kyc/<str:seller_id>/", seller_kyc_status),
    path("api/seller/kyc/upload/<str:seller_id>/", upload_kyc_document),
    path("api/seller/orders/<str:seller_id>/", seller_orders),
    path("api/seller/orders/stats/<str:seller_id>/", seller_orders_stats),
    path("api/seller/order/<str:order_id>/", seller_order_details),
    path("api/seller/order/update/<str:order_id>/", update_order_status),
    


]



