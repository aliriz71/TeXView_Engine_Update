from fastapi import APIRouter, File, UploadFile, HTTPException
# models
from models.users import User
from models.texviewpdf import TexviewPDF
from pydantic import BaseModel
from config.database import collection_name, collection_user_texviewpdf, collection_user #Database connection to MongoDB
from schema.schemas import list_serial, list_pdf_serial
from bson import ObjectId # Import ObjectId for MongoDB document IDs
from bson.binary import Binary  # Binary type for storing binary data in MongoDB
import hashlib
from datetime import datetime, timezone

from img_process.pdfMaster import pdf_conversion_bytes  # Import the pdf conversion function


router = APIRouter()

# GET Request method
@router.get("/")
async def get_users():
    users = list_serial(collection_name.find()) #.find() retrieves all documents of the collection
    return users

# POST Request method register a new user (temp)
# TODO: implement authentication and authorization via Auth0
@router.post("/register")
async def create_user_registration(user: User):
    print("User registration data:", user.email, user.password)

    result = collection_user.insert_one(dict(user))
    if result.inserted_id:
        print("User inserted with ID:", result.inserted_id)
        return {"message": "User registered successfully", "user_id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=500, detail="User registration failed")

# GET Request method for a specific user (temp)
# TODO: implement authentication and authorization via Auth0
# @router.get("/login", response_model=User, responses={404: {"description": "User Not found"}})
# async def get_user_for_login(email: str, password: str):
#     user = collection_user.find_one({"email": email, "password": password})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login", response_model=User, responses={404: {"description": "User Not found"}})
async def login_user(login_data: LoginRequest):
    user = collection_user.find_one({
        "email": login_data.email,
        "password": login_data.password
    })
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user



# # Put Request method
# @router.put("/{id}") #id from NoSQL database
# async def put_user(id: str, user: User):
#     collection_name.find_one_and_update({"_id": ObjectId(id)}, {"$set": dict(user)})  # Update the user with the given id

# # Delete Request method
# @router.delete("/{id}")
# async def delete_user(id: str):
#     collection_name.find_one_and_delete({"_id": ObjectId(id)})  # Delete the user with the given id


# Endpoints for documents and uploads
# 
# 

# Use Pydantic model for the response
# IMPORTANT: To make changes to pdf storage, you need to modify the TexviewPDF model and serialization(models/texviewpdf.py) (schema/schemas.py)
@router.post("/upload",response_model=TexviewPDF,status_code=201)
async def upload_texview_pdf(file: UploadFile = File(...)):
    contents = await file.read()

    # enforce PDF extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files allowed")

    # deterministic ID
    doc_id = hashlib.sha256(contents).hexdigest()

    # Do not need to store the file in the database, just the metadata
    # build the document with params
    mongo_doc = {
        "_id":        doc_id,
        "filename":   file.filename,
        "text":       "",  # Initially empty, will be filled after processing
        "latex":      None, 
        "uploaded_at": datetime.now(timezone.utc),
    }

    try:
        collection_user_texviewpdf.insert_one(mongo_doc)
    except Exception as e:
        raise HTTPException(500, f"DB insert failed: {e}")

    pdf_conversion_bytes(contents, doc_id)  # Process the PDF bytes to convert, annotate and extract text

    # FastAPI will automatically convert mongo_doc to TexviewPDF
    return mongo_doc
# GET Request method
@router.get("/documents")
async def list_documents():
    docs = list_pdf_serial(collection_user_texviewpdf.find()) #.find() retrieves all documents of the collection
    return docs


@router.get("/documents/{doc_id}",response_model=TexviewPDF,responses={404: {"description": "Not found"}})
async def get_document(doc_id: str):
    # geminiresponse = callgemini(extracteddata, "prompt")
    # generate latex from the prompt and change the doc.latex variable to the generated latex
    # to generate the latex, you need to call the Gemini API with the extracted data
    # and the prompt, and then set the doc.latex variable to the generated latex
    # alternatively the prompt can be be present in the function itself so you dont need to pass it as an argument
    # 

                                                        # exclude the binary payload
    doc = collection_user_texviewpdf.find_one({"_id": doc_id},{"data": 0})
    print(type(doc))
    # sample LaTeX content for testing
    doc["latex"] = r"""\section*{Sample LaTeX Content}

This is a simple test of LaTeX rendering. Here's a math formula:

\[
E = mc^2
\]
E = mc^2
\]

And here’s a small table:

\begin{tabular}{|c|c|}
\hline
\textbf{Fruit} & \textbf{Color} \\
\hline
Apple & Red \\
Banana & Yellow \\
Grapes & Purple \\
\hline
\end{tabular}

Let’s also try inline math like \( a^2 + b^2 = c^2 \).
"""

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc  # FastAPI + Pydantic will convert it into TexviewPDF  # get the doc with the given id