from datetime import datetime

def create_product_schema(data, image_urls, seller):

    return {
        "name": data.get("name"),
        "description": data.get("description"),
        "price": float(data.get("price")),
        "stock": int(data.get("stock")),

        "seller_id": seller["_id"],

        "seller": {
            "seller_name": seller.get("store_name"),
            "seller_rating": seller.get("rating"),
            "seller_location": seller.get("location")
        },

        "category": data.get("category"),

        "images": image_urls,

        "status": "stock",

        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }