import os

PORT = 8000
CONF_CONTENT_THRESHOLD = 0.2
IOU_CONTENT_THRESHOLD = 0.2

DEVICE = "cpu"
CORNER_MODEL_PATH = os.path.join("sources", "OCR", "weights", "corner.pt")
CONTENT_MODEL_PATH = os.path.join("sources", "OCR", "weights", "content.pt")
FACE_MODEL_PATH = os.path.join("sources", "OCR", "weights", "face.pt")

VGG_SEQ2_YML_PATH = os.path.join("sources", "OCR", "weights", "vgg-seq2seq.yml")
VGG_SEQ2_PTH_PATH = os.path.join("sources", "OCR", "weights", "vgg_seq2seq.pth")

UPLOAD_FOLDER = os.path.join("sources", "Input")
SAVE_DIR = os.path.join("sources", "Output")
