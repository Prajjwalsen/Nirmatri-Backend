from django.urls import path
from apps.sellers import views
from .views import superadmin_login, get_pending_sellers, approve_seller, all_sellers, reject_seller, admin_dashboard, recent_activities
from .import views
from .views import update_settings, get_settings, change_password, add_sub_admin
urlpatterns = [
    path("login/", superadmin_login),
    path("pending-sellers/", get_pending_sellers),
    path("seller/approve/<str:seller_id>/", approve_seller),
    path("sellers/", all_sellers),
    path("seller/reject/<str:seller_id>/", reject_seller),
    path("dashboard/", admin_dashboard),
    path("activities/", recent_activities),
    path("seller/<str:seller_id>/", views.seller_detail),
    path("settings/", get_settings),
    path("settings/update/", update_settings),
    path("change-password/", change_password),
    path("add-subadmin/", add_sub_admin),
    path("admins/",views.get_admins),
    path("update-role/",views.update_role),
]
