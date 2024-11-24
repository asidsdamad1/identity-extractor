import os
import requests
import sources.Controllers.config as cfg

from PIL import Image
from fastapi import Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from sources import app
from sources.Controllers import cccd
from sources.Controllers import utils
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:63342"],  # Add the frontend's origin here
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
@app.post("/api/scan/cccd")
async def scan_cccd(file: UploadFile = File(...)):
    try:
        print('# ====================================================')
        print('# File received: ', file.filename)
        print('# ====================================================')

        # Ensure the upload folder exists
        if not os.path.isdir(cfg.UPLOAD_FOLDER):
            os.makedirs(cfg.UPLOAD_FOLDER)

        file_path = os.path.join(cfg.UPLOAD_FOLDER, file.filename)

        # Save the uploaded file to the server
        with open(file_path, "wb") as f:
            content = await file.read()  # Read file content
            f.write(content)  # Save file to the path

        # Check file format
        if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            error = "This file is not supported!"
            return JSONResponse(status_code=200, content={"code": 404, "message": error})

        # Optimize images for sharpness, smoothness, and contrast
        await utils.image_optimal_advance(file_path)

        # Extract information from the file
        return await extract_info(file_path)

    except Exception as ex:
        print("Error occurred in scan_cccd: ", ex)
        raise HTTPException(status_code=500, detail="Internal server error")


async def extract_info(file_path: str = None):
    if not os.path.isdir(cfg.UPLOAD_FOLDER):
        os.mkdir(cfg.UPLOAD_FOLDER)

    if file_path is None:
        error = "Missing file name! Detecting content failed!"
        return JSONResponse(status_code=200, content={"code": 402, "message": error})

    # get data info from qr code
    data_qr_code = await cccd.extract_info_qr_code(file_path)

    # get data info from boxes
    data_extract = await cccd.extract_info_boxes(file_path)

    if data_qr_code is None:
        if data_extract is None:
            error = "Missing fields! Detecting content failed!"
            return JSONResponse(status_code=200, content={"code": 402, "message": error})

    data_final = {
        'extract': data_extract,
        'qrCode': data_qr_code
    }

    return JSONResponse(status_code=200, content={"code": 0, "message": "OK", "data": data_final})

