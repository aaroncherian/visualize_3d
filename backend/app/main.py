import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import traceback
from starlette.middleware.cors import CORSMiddleware
import numpy as np
import pandas as pd
from pathlib import Path
import logging
import base64

import subprocess
import shlex


from skellymodels.create_model_skeleton import create_mediapipe_skeleton_model, create_openpose_skeleton_model
from skellymodels.model_info.mediapipe_model_info import MediapipeModelInfo

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# recording_folder_path = Path(r'C:\Users\aaron\FreeMocap_Data\recording_sessions\freemocap_test_data')
recording_folder_path = Path(r'D:\2023-05-17_MDN_NIH_data\1.0_recordings\calib_3\sesh_2023-05-17_13_37_32_MDN_treadmill_1')
# recording_folder_path = Path(r'C:\Users\aaron\FreeMocap_Data\recording_sessions\freemocap_sample_data')
output_data_folder_path = recording_folder_path / 'output_data'
tracker_type = 'mediapipe'
data_3d_path = output_data_folder_path / f'{tracker_type}_body_3d_xyz.npy'

video_name = recording_folder_path/'test_video.mp4'

# Global variable to store frames
frames = {}

@asynccontextmanager
async def lifespan_manager(app:FastAPI):
    logger.info("Starting up FastAPI app - access API backend interface at http://localhost:8000/docs")
    yield
    logger.info("Shutting down FastAPI app")

app = FastAPI(lifespan=lifespan_manager)

origins = ["http://localhost:5173"]  
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount("/static", StaticFiles(directory="skeleton-visualization/fast_api"), name="static")
from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from tqdm import tqdm
import time


@app.post("/upload-frames")
async def upload_frames(request: Request, background_tasks: BackgroundTasks):
    global frames
    try:
        start_time = time.time()
        form = await request.form()
        files = form.getlist("files")
        width = int(form.get("width", 0))
        height = int(form.get("height", 0))
        batch_index = int(form.get("batchIndex", 0))
        total_frames = int(form.get("totalFrames", 0))

        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")
        if width == 0 or height == 0:
            raise HTTPException(status_code=400, detail="Invalid width or height")

        logger.info(f"Received batch {batch_index} with {len(files)} files. Total frames: {total_frames}")

        for i, file in enumerate(files):
            frame_number = batch_index * 500 + i  # Assuming 500 frames per batch
            contents = await file.read()
            nparr = np.frombuffer(contents, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            frames[frame_number] = img

        logger.info(f"Processed batch {batch_index} in {time.time() - start_time:.2f} seconds")
        logger.info(f"Received {len(frames)} frames out of {total_frames} expected.")

        if len(frames) >= total_frames:
            logger.info("All frames received. Starting video creation.")
            background_tasks.add_task(create_video_from_frames, video_name, total_frames, width, height)
            return JSONResponse(status_code=202, content={'status': 'processing', 'message': 'Video creation started'})
        else:
            return JSONResponse(status_code=200, content={'status': 'success', 'message': f'Batch {batch_index} received'})

    except Exception as e:
        logger.error(f"Error in upload_frames: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/")
async def get_index():
    logger.info("Serving index.html")
    return FileResponse("backend/static/index.html")

    
@app.get("/data")
async def get_data():
    try:
        np_data = np.load(data_3d_path)

        if tracker_type == 'mediapipe':
            skeleton = create_mediapipe_skeleton_model()
        else:
            raise HTTPException(status_code=400, detail="Unknown tracker type")
        
        skeleton.integrate_freemocap_3d_data(np_data)
        return skeleton.to_custom_dict()
    except Exception as e:
        logger.error(f"Error serving data: {e}")
        raise HTTPException(status_code=500, detail=f"Error serving data: {e}")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


import subprocess
import logging
from tqdm import tqdm

def create_video_from_frames(output_filename, total_frames, width, height):
    global frames
    try:
        start_time = time.time()
        logger.info(f"Starting video creation with {total_frames} frames")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_filename), fourcc, 25.0, (width, height))

        for i in tqdm(range(total_frames), desc="Creating video"):
            frame = frames.get(i)
            if frame is not None:
                out.write(frame)
            else:
                logger.warning(f"Missing frame: {i}")

        out.release()
        logger.info(f"Video saved as {output_filename}")
        logger.info(f"Video creation completed in {time.time() - start_time:.2f} seconds")

        # Clear the frames from memory
        frames.clear()
        logger.info("Cleared frames from memory")

    except Exception as e:
        logger.error(f"Error in create_video_from_frames: {str(e)}")
    finally:
        # Ensure frames are cleared even if an error occurred
        frames.clear()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")