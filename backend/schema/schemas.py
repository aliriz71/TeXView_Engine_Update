# Connect object to dictionary for serialization
# This file is used to convert user objects to dictionaries for easier handling in responses.
def individual_serial(user) -> dict:
    return {
        "id": str(user["_id"]), #_id is mongo's generated ObjectId
        "email": user["email"],
        "password": user["password"],
    }

def list_serial(users) -> list:
    return [individual_serial(user) for user in users]

def individual_pdf_serial(doc) -> dict:
    return {
        "id":           str(doc["_id"]),
        "filename":     doc["filename"],
        "text":         doc["text"],
        "latex":        doc.get("latex"),
        "uploaded_at":  doc.get("uploaded_at").isoformat(),
    }

def list_pdf_serial(docs) -> list:
    return [individual_pdf_serial(d) for d in docs]