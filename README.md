## Overview
This project is a FastAPI-based application for extracting information from CCCD (Citizen Identification) cards using OCR (Optical Character Recognition) and QR code scanning.

## Features

- Upload CCCD images for processing.
- Extract information from QR codes on CCCD cards.
- Extract information from text boxes on CCCD cards using YOLOv5 and VietOCR.
- Image optimization for better OCR results.
- API endpoints for integration with other systems.


## Python
- **Version**: 3.11.0
- **Download URL**: [Python 3.11.0](https://www.python.org/downloads/release/python-3110/)

## Setup Commands
1. Create a virtual environment:
    ```sh
    python -m venv venv
    ```
2. Activate the virtual environment:
    - On Windows:
        ```sh
        venv\Scripts\activate
        ```
    - On Unix or MacOS:
        ```sh
        source venv/bin/activate
        ```
3. Upgrade `pip`:
    ```sh
    python -m pip install --upgrade pip
    ```
4. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```
5. Run the application:
    ```sh
    python run.py
    ```
