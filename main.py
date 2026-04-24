from supabase import create_client, Client
import os
from fastapi import FastAPI, UploadFile, File
import boto3
import os

app = FastAPI()

# ENV VARIABLES (le mettiamo dopo su Railway)
# R2
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_BUCKET = "slabreality"
R2_ENDPOINT = os.getenv("R2_ENDPOINT")  # tipo https://xxxx.r2.cloudflarestorage.com
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL")  # tipo https://pub-xxx.r2.dev

# SUPABASE
SUPABASE_URL = "https://qzxcazacujjieafoqbrh.supabase.co"
SUPABASE_KEY = "sb_publishable_7NZtJmgog-Z5FO_-Y39LxA_IV7YbPZW"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

s3 = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY
)

@app.get("/")
def root():
    return {"status": "SlabReality API is running"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_bytes = await file.read()

    s3.put_object(
        Bucket=R2_BUCKET,
        Key=file.filename,
        Body=file_bytes,
        ContentType=file.content_type
    )

    return {
        "filename": file.filename,
        "url": f"{R2_PUBLIC_URL}/{file.filename}"
    }
