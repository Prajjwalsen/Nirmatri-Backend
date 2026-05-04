from django.contrib import admin
from django.urls import path, include
    # ← IMPORTANT
   


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/user/", include("apps.users.urls")),  
    path("api/seller/", include("apps.sellers.urls")),
    path("", include("apps.core.urls")),
    path("api/auth/", include("authapp.urls")),
    path("api/auth/", include("apps.users.googleauth.urls")),
    path("api/admin/", include("apps.superadmin.urls")),
    path("api/products/", include("apps.products.urls")),
    path("api/super/", include("apps.superadmin.urls")),
  
]

