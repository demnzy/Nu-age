# routers/media.py
import logging
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from services.bunny_service import upload_video_to_stream, upload_audio_to_bunny

# Set up logging so you can see real errors in your terminal, without exposing them to users
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/media", tags=["Media Handling"])

@router.post('/upload/video')
async def upload_video_only(file: UploadFile = File(...)):
    """Uploads a video to Bunny Stream and returns the embed URL."""
    
    # OPTIMIZATION 1: Early Exit. Prevent allocating memory if the user uploads a non-video file.
    if file.content_type and not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Video expected.")

    try:
        video_bytes = await file.read()
        video_url = await upload_video_to_stream(video_bytes, file.filename)
        return {"type": "video", "url": video_url}
        
    except Exception as e:
        # OPTIMIZATION 2: Secure logging. Log the actual crash for you, return a safe 500 to the client.
        logger.error(f"Video upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during video upload.")
        
    finally:
        # OPTIMIZATION 3: Memory release. UploadFile uses disk/RAM spools. Closing it frees the OS file descriptor immediately.
        await file.close()


@router.post('/upload/private-asset')
async def upload_private_asset(
    course_id: str = Form(...), 
    type: str = Form(...), 
    file: UploadFile = File(...)
):
    """Uploads audio/documents to Edge Storage and returns the internal path."""
    
    # OPTIMIZATION 4: Anti-Directory Traversal. Because 'type' dictates the folder path, 
    # we must validate it here since we are keeping it as a standard string parameter.
    if type not in ["audio", "document"]:
        raise HTTPException(status_code=400, detail="Asset type must be 'audio' or 'document'.")

    try:
        # OPTIMIZATION 5: Bulletproof extension extraction. 
        # file.filename.split(".")[-1] breaks on files with no extension or multiple dots (e.g., file.tar.gz).
        ext = Path(file.filename).suffix if file.filename else ""
        if not ext:
            raise HTTPException(status_code=400, detail="File must have a valid extension.")
            
        safe_name = f"{type}_{uuid.uuid4().hex}{ext}"
        
        # Route to the correct folder based on type safely
        folder_path = f"courses/{course_id}/{type}s" 
        
        asset_bytes = await file.read()
        internal_path = await upload_audio_to_bunny(asset_bytes, safe_name, folder_path)
        
        return {"type": type, "path": internal_path}
        
    except HTTPException:
        # Let our expected 400 errors pass through normally
        raise 
    except Exception as e:
        logger.error(f"Asset upload failed for course {course_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during asset upload.")
        
    finally:
        # OPTIMIZATION 3: Memory release.
        await file.close()