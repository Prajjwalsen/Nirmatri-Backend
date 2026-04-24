import cloudinary.uploader
from pymongo import MongoClient
from bson import ObjectId
import os
from apps.db.mongo.connection import MONGO_URI
from .schemas import create_product_schema
from django.conf import settings

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["nirmatriDB"]


products_collection = db["products"]
sellers_collection = db["sellers"]


def create_product_service(data, files, seller_id):

    seller = sellers_collection.find_one({"_id": ObjectId(seller_id)})

    if not seller:
        return {"error": "Seller not found"}, 404

    image_urls = []

    for image in files.getlist("images"):

        result = cloudinary.uploader.upload(image)

        image_urls.append(result["secure_url"])

    product = create_product_schema(data, image_urls, seller)

    result = products_collection.insert_one(product)

    product["_id"] = str(result.inserted_id)

    return {"product": product}, 201