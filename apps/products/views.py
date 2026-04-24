import json
import uuid
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import create_product_service
from apps.db.mongo.connection import db   # make sure this exists

products = db["products"]

# =====================================
# CREATE PRODUCT (SERVICE BASED)
# =====================================
@csrf_exempt
def create_product(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    seller_id = request.POST.get("seller_id")

    if not seller_id:
        return JsonResponse({"error": "seller_id is required"}, status=400)

    response, status = create_product_service(
        request.POST,
        request.FILES,
        seller_id
    )

    return JsonResponse(response, status=status)


# =====================================
# GET SELLER PRODUCTS
# =====================================
def seller_products(request, seller_id):

    data = list(products.find({"seller_id": seller_id}))

    for p in data:
        p["_id"] = str(p["_id"])

    return JsonResponse(data, safe=False)


# =====================================
# PRODUCT STATS
# =====================================
def seller_products_stats(request, seller_id):

    total = products.count_documents({"seller_id": seller_id})

    active = products.count_documents({
        "seller_id": seller_id,
        "status": "active"
    })

    low_stock = products.count_documents({
        "seller_id": seller_id,
        "stock": {"$lt": 5}
    })

    out_stock = products.count_documents({
        "seller_id": seller_id,
        "stock": 0
    })

    return JsonResponse({
        "total": total,
        "active": active,
        "low_stock": low_stock,
        "out_stock": out_stock
    })


# =====================================
# ADD PRODUCT (DIRECT)
# =====================================
@csrf_exempt
def add_product(request, seller_id):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    try:
        data = request.POST
        images = request.FILES.getlist("images")

        product = {
            "product_id": "PROD-" + str(uuid.uuid4())[:6],
            "seller_id": seller_id,
            "name": data.get("name"),
            "category": data.get("category"),
            "price": float(data.get("price", 0)),
            "stock": int(data.get("stock", 0)),
            "status": data.get("status", "active"),
            "description": data.get("description"),
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "images": []
        }

        # Save images safely
        for img in images:
            unique_name = f"{uuid.uuid4()}_{img.name}"
            file_path = f"media/products/{unique_name}"

            with open(file_path, "wb+") as f:
                for chunk in img.chunks():
                    f.write(chunk)

            product["images"].append(file_path)

        products.insert_one(product)

        return JsonResponse({
            "message": "Product added successfully",
            "product_id": product["product_id"]
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# =====================================
# UPDATE PRODUCT
# =====================================
@csrf_exempt
def update_product(request, product_id):

    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required"}, status=405)

    try:
        data = json.loads(request.body)

        products.update_one(
            {"product_id": product_id},
            {"$set": data}
        )

        return JsonResponse({"message": "Product updated"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# =====================================
# DELETE PRODUCT
# =====================================
@csrf_exempt
def delete_product(request, product_id):

    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE request required"}, status=405)

    try:
        products.delete_one({"product_id": product_id})

        return JsonResponse({"message": "Product deleted"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)