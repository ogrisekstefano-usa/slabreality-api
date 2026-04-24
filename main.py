from supabase import create_client, Client
import os
from fastapi import FastAPI, UploadFile, File, Form
import boto3
import uuid

app = FastAPI()

# =========================
# ENV VARIABLES
# =========================

# R2 (Cloudflare)
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_BUCKET = os.getenv("R2_BUCKET")
R2_ENDPOINT = os.getenv("R2_ENDPOINT")
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# =========================
# CLIENTS (init a startup)
# =========================

supabase: Client = None
s3 = None

@app.on_event("startup")
def startup():
    global supabase, s3

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    s3 = boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY
    )

    print("🔥 Supabase e R2 inizializzati")


# =========================
# TEST
# =========================

@app.get("/")
def root():
    return {"status": "API running"}


# =========================
# CREATE MATERIAL (solo dati)
# =========================

from pydantic import BaseModel

class Material(BaseModel):
    name: str
    category: str
    color: str
    finish: str
    image_url: str


@app.post("/materials")
def create_material(material: Material):
    try:
        response = supabase.table("materials").insert({
            "name": material.name,
            "category": material.category,
            "color": material.color,
            "finish": material.finish,
            "image_url": material.image_url
        }).execute()

        return response.data

    except Exception as e:
        return {"error": str(e)}


# =========================
# GET MATERIALS
# =========================

@app.get("/materials")
def get_materials():
    data = supabase.table("materials").select("*").execute()
    return data.data


# =========================
# UPLOAD FILE SOLO
# =========================

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        filename = f"{uuid.uuid4()}-{file.filename}"

        s3.put_object(
            Bucket=R2_BUCKET,
            Key=filename,
            Body=file_bytes,
            ContentType=file.content_type
        )

        return {
            "filename": filename,
            "url": f"{R2_PUBLIC_URL}/{filename}"
        }

    except Exception as e:
        return {"error": str(e)}


# =========================
# CREA MATERIAL + UPLOAD (TOP)
# =========================

@app.post("/materials/upload")
async def create_material_with_file(
    name: str = Form(...),
    category: str = Form(...),
    color: str = Form(...),
    finish: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        file_bytes = await file.read()
        filename = f"{uuid.uuid4()}-{file.filename}"

        # upload su R2
        s3.put_object(
            Bucket=R2_BUCKET,
            Key=filename,
            Body=file_bytes,
            ContentType=file.content_type
        )

        image_url = f"{R2_PUBLIC_URL}/{filename}"

        # salva su Supabase
        response = supabase.table("materials").insert({
            "name": name,
            "category": category,
            "color": color,
            "finish": finish,
            "image_url": image_url
        }).execute()

        return response.data

    except Exception as e:
        return {"error": str(e)}
