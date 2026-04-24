#Seller Register API
import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from apps.db.mongo.db_collections import sellers_collection
from apps.sellers.services import seller_login_service
from datetime import datetime
from django.http import JsonResponse
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["nirmatri"]
#=======================
#register API

@csrf_exempt
@require_POST
def seller_register(request):
    try:
        data = json.loads(request.body)

        fullname = data.get("fullname")
        email = data.get("email")
        password = data.get("password")

        # ================= VALIDATION =================
        missing = []
        for field in ["fullname", "email", "password"]:
            if not data.get(field):
                missing.append(field)

        if missing:
            return JsonResponse(
                {"error": "Missing fields", "fields": missing},
                status=400
            )

        # ================= DUPLICATE CHECK =================
        if sellers_collection.find_one({"email": email}):
            return JsonResponse(
                {"error": "Seller already registered with this email"},
                status=409
            )

        # ================= SAVE TO DB =================
        seller_doc = {
            "full_name": fullname,
            "email": email,
            "password": password,  # 🔒 Later hash karenge
            "status": "pending",   # 👈 SUPERADMIN APPROVAL
            "created_at": datetime.utcnow(),
            "approved_at": None,
            "approved_by": None
        }

        sellers_collection.insert_one(seller_doc)

        return JsonResponse(
            {
                "message": "Seller registered successfully",
                "status": "pending",
                "note": "Your account will be activated after admin approval"
            },
            status=201
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    except Exception as e:
        print("SELLER REGISTER ERROR:", str(e))
        return JsonResponse(
            {"error": "Server error", "details": str(e)},
            status=500
        )
#====================================
#=======seller onboarding API========

@csrf_exempt
def seller_onboarding(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)

        print(data)

        seller_doc = {
            # STORE INFO
            "store_name": data.get("storeName"),
            "owner_name": data.get("ownerName"),
            "store_category": data.get("storeCategory", []),

            # KYC
            "pan_number": data.get("panNumber"),
            "aadhaar_number": data.get("aadhaarNumber"),

            # BANK
            "account_holder": data.get("accountHolderName"),
            "account_number": data.get("accountNumber"),
            "ifsc_code": data.get("ifscCode"),
            "bank_name": data.get("bankName"),

            # PHONE
            "phone_number": data.get("phoneNumber"),

            # STATUS
            "status": "pending",
            "created_at": datetime.utcnow(),
        }

        sellers_collection.insert_one(seller_doc)

        return JsonResponse({
            "message": "Seller onboarding completed",
            "status": "pending_approval"
        }, status=201)

    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=500)
    
#=======================
#seller login API

@csrf_exempt
def seller_login(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    data = json.loads(request.body)

    response, status = seller_login_service(data)

    return JsonResponse(response, status=status)

  #=======================
  #seller dashboard API
  
orders = db["orders"]
products = db["products"]

def seller_dashboard(request, seller_id):

    # total orders
    total_orders = orders.count_documents({"seller_id": seller_id})

    # active products
    active_products = products.count_documents({
        "seller_id": seller_id,
        "status": "active"
    })

    # pending orders
    pending_orders = orders.count_documents({
        "seller_id": seller_id,
        "status": "pending"
    })

    # total earnings
    revenue = 0
    seller_orders = orders.find({"seller_id": seller_id})

    for order in seller_orders:
        revenue += order.get("amount", 0)

    return JsonResponse({
        "total_orders": total_orders,
        "active_products": active_products,
        "pending_orders": pending_orders,
        "revenue": revenue
    })


# ==============================
# SELLER BANK DETAILS
# ==============================

sellers = db["sellers"]
transactions = db["transactions"]

def seller_bank_details(request, seller_id):

    # GET BANK DETAILS
    if request.method == "GET":

        seller = sellers.find_one({"seller_id": seller_id})

        if not seller:
            return JsonResponse({"error": "Seller not found"}, status=404)

        return JsonResponse(seller.get("bankDetails", {}))


    # UPDATE BANK DETAILS
    elif request.method == "POST":

        data = json.loads(request.body)

        sellers.update_one(
            {"seller_id": seller_id},
            {"$set": {"bankDetails": data}},
            upsert=True
        )

        return JsonResponse({"message": "Bank details updated"})


# ==============================
# SELLER TRANSACTIONS
# ==============================
def seller_transactions(request, seller_id):

    txns = list(transactions.find({"seller_id": seller_id}))

    for t in txns:
        t["_id"] = str(t["_id"])

    return JsonResponse(txns, safe=False)

#=====================
#seller kyc status API

kyc = db["kyc"]
def seller_kyc_status(request, seller_id):

    data = kyc.find_one({"seller_id": seller_id})

    if not data:
        return JsonResponse({"documents": []})

    data["_id"] = str(data["_id"])

    return JsonResponse(data)

#seller kyc upload API

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def upload_kyc_document(request, seller_id):

    if request.method == "POST":

        document_type = request.POST.get("type")
        file = request.FILES.get("file")

        # file save logic
        file_url = "/media/" + file.name

        kyc.update_one(
            {"seller_id": seller_id},
            {
                "$push": {
                    "documents": {
                        "type": document_type,
                        "file": file_url,
                        "status": "pending"
                    }
                }
            },
            upsert=True
        )

        return JsonResponse({"message": "Document uploaded"})
    
#=====================
# Additional seller APIs (orders list, order stats, order details, update order status)


# =====================================
# SELLER ORDERS LIST
# =====================================
def seller_orders(request, seller_id):

    data = list(orders.find({"seller_id": seller_id}))

    for order in data:
        order["_id"] = str(order["_id"])

    return JsonResponse(data, safe=False)


# =====================================
# SELLER ORDER STATS
# =====================================
def seller_orders_stats(request, seller_id):

    total = orders.count_documents({"seller_id": seller_id})
    pending = orders.count_documents({"seller_id": seller_id, "status": "pending"})
    processing = orders.count_documents({"seller_id": seller_id, "status": "processing"})
    shipped = orders.count_documents({"seller_id": seller_id, "status": "shipped"})
    delivered = orders.count_documents({"seller_id": seller_id, "status": "delivered"})

    return JsonResponse({
        "total": total,
        "pending": pending,
        "processing": processing,
        "shipped": shipped,
        "delivered": delivered
    })


# =====================================
# SINGLE ORDER DETAILS
# =====================================
def seller_order_details(request, order_id):

    order = orders.find_one({"_id": order_id})

    if not order:
        return JsonResponse({"error": "Order not found"})

    order["_id"] = str(order["_id"])

    return JsonResponse(order)


# =====================================
# UPDATE ORDER STATUS
# =====================================
def update_order_status(request, order_id):

    data = json.loads(request.body)

    new_status = data.get("status")

    orders.update_one(
        {"_id": order_id},
        {"$set": {"status": new_status}}
    )

    return JsonResponse({"message": "Order status updated"})

