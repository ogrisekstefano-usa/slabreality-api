from fastapi import FastAPI, UploadFile, File
import os

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/")
def root():
    return {"status": "SlabReality API is running"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return {
        "filename": file.filename,
        "url": f"/files/{file.filename}"
    }

@app.get("/files/{filename}")
def get_file(filename: str):
    return {"file_url": f"/uploads/{filename}"}
