import jwt
from datetime import datetime
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests
from apps.users.utils import verify_password  
from apps.db.mongo.connection import users_collection
 

def verify_google_token(token):
    return id_token.verify_oauth2_token(
        token,
        requests.Request(),
        settings.GOOGLE_CLIENT_ID
    )



def user_login_service(data):

    email = data.get("email")
    password = data.get("password")

    user = users_collection.find_one({"email": email})

    if not user:
        return {"error": "User not found"}, 404

    if not verify_password(password, user["password"]):
        return {"error": "Invalid password"}, 401

    # JWT token
    token = jwt.encode(
        {"user_id": str(user["_id"])},
        settings.SECRET_KEY,
        algorithm="HS256"
    )

    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "id": str(user["_id"]),
            "name": user.get("full_name"),
            "email": user.get("email"),
            "phone": user.get("phone")
        }
    }, 200