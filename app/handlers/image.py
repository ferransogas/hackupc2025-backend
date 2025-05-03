from fastapi import APIRouter, File, UploadFile, HTTPException
import shutil
import tempfile
import os

router = APIRouter()

@router.post("/image")
async def process_image(image_file: UploadFile = File(...)):
    # Validate file type
    content_type = image_file.content_type
    if not content_type or not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Create a temporary file to store the uploaded image
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image_file.filename)[1]) as temp_image:
        # Copy the uploaded file content to the temporary file
        shutil.copyfileobj(image_file.file, temp_image)
        image = temp_image.name

    return "Image processed successfully"