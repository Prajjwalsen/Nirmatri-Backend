import json
import jwt
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.db.mongo import db
from bson import ObjectId
from apps.db.mongo.connection import superadmin_collection


SECRET_KEY = "8f7d9c2a1b3e4f5a6c7d8e9f0a1b2c3d4"


# ==============================
# SUPERADMIN LOGIN
# ==============================

@csrf_exempt
def superadmin_login(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    data = json.loads(request.body)

    email = data.get("email")
    password = data.get("password")

    admin = superadmin_collection.find_one({"email": email})

    if not admin:
        return JsonResponse({"error": "Admin not found"}, status=404)

    if admin["password"] != password:
        return JsonResponse({"error": "Invalid password"}, status=401)

    payload = {
        "admin_id": str(admin["_id"]),
        "email": admin["email"],
        "role": "superadmin",
        "exp": datetime.utcnow() + timedelta(hours=24)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return JsonResponse({
        "message": "Login successful",
        "token": token
    })

# ==============================
# GET ALL SELLERS
# ==============================

def all_sellers(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET request required"}, status=405)

    data = list(sellers.find())

    for s in data:
        s["_id"] = str(s["_id"])

    return JsonResponse({"sellers": data})


# ==============================
# GET PENDING SELLERS
# ==============================

def get_pending_sellers(request):

    if request.method != "GET":
        return JsonResponse({
            "error": "GET request required"
        }, status=405)

    data = list(sellers.find({"status": "pending"}))

    for s in data:
        s["_id"] = str(s["_id"])

    return JsonResponse({"pending_sellers": data})


# ==============================
# APPROVE SELLER
# ==============================
@csrf_exempt
def approve_seller(request, seller_id):

    sellers.update_one(
        {"_id": ObjectId(seller_id)},
        {"$set": {"status": "approved"}}
    )

    return JsonResponse({"message": "Seller approved"})
# ==============================
# REJECT SELLER
# ==============================

@csrf_exempt
def reject_seller(request, seller_id):

    sellers.update_one(
        {"_id": ObjectId(seller_id)},
        {"$set": {"status": "rejected"}}
    )

    return JsonResponse({"message": "Seller rejected"})

# ==============================
# ADMIN DASHBOARD
# ==============================

products = db["products"]
orders = db["orders"]
sellers = db["sellers"]


def admin_dashboard(request):

    total_sellers = sellers.count_documents({})

    pending_sellers = sellers.count_documents({
        "status": "pending"
    })

    total_products = products.count_documents({})

    revenue = 0

    # calculate revenue
    for order in orders.find({}):

        revenue += order.get("total_price", 0)   # <-- important

    return JsonResponse({

        "total_sellers": total_sellers,
        "pending_sellers": pending_sellers,
        "products": total_products,
        "revenue": revenue

    })
# ==============================
# RECENT ACTIVITIES FOR ADMIN DASHBOARD
# ==============================
def recent_activities(request):

    activities = []

    # New Sellers
    for s in sellers.find().sort("_id", -1).limit(3):
        activities.append({
            "action": "New seller registered",
            "time": "Recently",
            "status": "success"
        })

    # Approved Sellers
    for s in sellers.find({"status": "approved"}).sort("_id", -1).limit(2):
        activities.append({
            "action": "Seller approved",
            "time": "Recently",
            "status": "success"
        })

    # Orders
    for o in orders.find().sort("_id", -1).limit(2):
        activities.append({
            "action": "Payment processed",
            "time": "Recently",
            "status": "success"
        })

    return JsonResponse({"activities": activities})

# ==============================
# GET SELLER DETAILS    
# ==============================
from django.http import JsonResponse
from bson import ObjectId
from apps.db.mongo import db

sellers = db["sellers"]

def seller_detail(request, seller_id):

    seller = sellers.find_one({"_id": ObjectId(seller_id)})

    if not seller:
        return JsonResponse({"error": "Seller not found"}, status=404)

    seller["_id"] = str(seller["_id"])

    return JsonResponse({
        "seller": seller
    })

# ==============================
# CHANGE PASSWORD   
#=============================
admins = db["superadmins"]

@csrf_exempt
def change_password(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)

    admin_id = data.get("admin_id")
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    admin = admins.find_one({"_id": ObjectId(admin_id)})

    if admin["password"] != old_password:
        return JsonResponse({"error": "Wrong password"}, status=400)

    admins.update_one(
        {"_id": ObjectId(admin_id)},
        {"$set": {"password": new_password}}
    )

    return JsonResponse({"message": "Password updated"})

# ==============================
# ADD SUB ADMIN 
# ==============================
@csrf_exempt
def add_sub_admin(request):

    data = json.loads(request.body)

    admins.insert_one({
        "name": data["name"],
        "email": data["email"],
        "password": data["password"],
        "role": "subadmin"
    })

    return JsonResponse({"message": "Sub Admin Created"})

# ==============================
#ROLE MANAGEMENT
# ==============================
def get_admins(request):

    data = list(admins.find())

    for a in data:
        a["_id"] = str(a["_id"])

    return JsonResponse({"admins": data})
# ==============================
# UPDATE ROLE
# ==============================
@csrf_exempt
def update_role(request):

    data = json.loads(request.body)

    superadmin_collection.update_one(
        {"_id":ObjectId(data["admin_id"])},
        {"$set":{"role":data["role"]}}
    )

    return JsonResponse({"message":"Role updated"})
# ==============================
# GET SETTINGS      
# ==============================
settings_collection = db["settings"]

def get_settings(request):

    settings = settings_collection.find_one({"type": "system"})

    if not settings:
        settings = {
            "emailNotifications": True,
            "twoFactorAuth": False,
            "autoApprove": False,
            "maintenanceMode": False
        }

    settings.pop("_id", None)

    return JsonResponse(settings)
# ==============================
# UPDATE SETTINGS

@csrf_exempt
def update_settings(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)

    settings_collection.update_one(
        {"type": "system"},
        {"$set": data},
        upsert=True
    )

    return JsonResponse({"message": "Settings updated"})
   