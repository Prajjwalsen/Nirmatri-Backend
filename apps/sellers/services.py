from .mongo_services import get_seller_by_email
from apps.db.mongo.utils import verify_password
from django.conf import settings
import jwt
from datetime import datetime, timedelta
from apps.db.mongo.db_collections import sellers_collection





def seller_login_service(data):

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return {"error": "Email and password required"}, 400

    seller = sellers_collection.find_one({"email": email})

    if not seller:
        return {"error": "Seller not found"}, 404

    # TEMP PASSWORD CHECK
    if password != seller["password"]:
        return {"error": "Invalid password"}, 401

    status = seller.get("status")

    if status == "pending":
        return {
            "error": "Your registration is under process. Please wait for chacha approval."
        }, 403

    if status == "rejected":
        return {
            "error": "Your seller account has been rejected."
        }, 403

    payload = {
        "seller_id": str(seller["_id"]),
        "email": seller["email"],
        "exp": datetime.utcnow() + timedelta(days=7)
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    return {
        "message": "Login successful",
        "token": token,
        "seller": {
            "id": str(seller["_id"]),
            "email": seller["email"],
            "full_name": seller.get("full_name"),
            "status": seller["status"]
        }
    }, 200