import os
import numpy as np
import yolov5
import sources.Controllers.config as cfg
import cv2

from PIL import Image
from qreader import QReader
from vietocr.tool.config import Cfg as CfgVietOCR
from vietocr.tool.predictor import Predictor
from sources.Controllers import utils
from qreader import QReader
from cv2 import QRCodeDetector, imread

GLB_FACE_MODEL = yolov5.load(cfg.FACE_MODEL_PATH)
GLB_CORNER_MODEL = yolov5.load(cfg.CORNER_MODEL_PATH)

GLB_CONTENT_MODEL = yolov5.load(cfg.CONTENT_MODEL_PATH)
GLB_CONTENT_MODEL.conf = cfg.CONF_CONTENT_THRESHOLD
GLB_CONTENT_MODEL.iou = cfg.IOU_CONTENT_THRESHOLD

GLB_UPLOAD_FOLDER = cfg.UPLOAD_FOLDER
GLB_SAVE_DIR = cfg.SAVE_DIR

glb_config = CfgVietOCR.load_config_from_file(cfg.VGG_SEQ2_YML_PATH)
glb_config["pretrain"] = cfg.VGG_SEQ2_PTH_PATH
glb_config["weights"] = cfg.VGG_SEQ2_PTH_PATH
glb_config["cnn"]["pretrained"] = False
glb_config["device"] = cfg.DEVICE
glb_config["predictor"]["beamsearch"] = False
glb_detector = Predictor(glb_config)
glb_qreader = QReader()
# qreader_reader, cv2_reader, pyzbar_reader = QReader(), cv2.QRCodeDetector(), decode

async def extract_info_qr_code(file_path: str = None):
    data_final = None
    try:
        imageQrCode = cv2.cvtColor(cv2.imread(file_path), cv2.COLOR_BGR2RGB)
        decoded_text = glb_qreader.detect_and_decode(image=imageQrCode)

        if decoded_text and decoded_text[0] is not None:
            FIELDS_DETECTED = list(decoded_text)[0].split('|')
            if len(FIELDS_DETECTED) == 7:
                name = FIELDS_DETECTED[2]
                try: 
                    name = name.encode('shift-jis').decode('utf-8')
                except Exception as ex:
                    name = FIELDS_DETECTED[2]
                data_final = {
                    'noCccd': FIELDS_DETECTED[0],
                    'noCmnd': FIELDS_DETECTED[1],
                    'name': name,
                    'dob': FIELDS_DETECTED[3][:2] + '/' + FIELDS_DETECTED[3][2:][:2] + '/' + FIELDS_DETECTED[3][4:],
                    'sex': FIELDS_DETECTED[4],
                    'address': FIELDS_DETECTED[5],
                    'releaseDate': FIELDS_DETECTED[6][:2] + '/' + FIELDS_DETECTED[6][2:][:2] + '/' + FIELDS_DETECTED[6][4:]
                }

    except Exception as ex:
        print("Loi me no roi cccd chip qr code: ", ex)

    return data_final

async def extract_info_boxes(file_path: str = None):
    data_final = None
    try:
        CORNER = GLB_CORNER_MODEL(file_path)
        predictions = CORNER.pred[0]
        categories = predictions[:, 5].tolist()
        if len(categories) != 4:
            return None

        boxes = utils.class_order(predictions[:, :4].tolist(), categories)
        IMG = Image.open(file_path)
        center_points = list(map(utils.get_center_point, boxes))

        c2, c3 = center_points[2], center_points[3]
        c2_fix, c3_fix = (c2[0], c2[1] + 30), (c3[0], c3[1] + 30)

        center_points = [center_points[0], center_points[1], c2_fix, c3_fix]
        center_points = np.asarray(center_points)

        aligned = utils.four_point_transform(IMG, center_points)
        aligned = Image.fromarray(aligned)

        CONTENT = GLB_CONTENT_MODEL(aligned)
        predictions = CONTENT.pred[0]
        categories = predictions[:, 5].tolist()

        boxes = predictions[:, :4].tolist()
        boxes, categories = utils.non_max_suppression_fast(np.array(boxes), categories, 0.5)
        boxes = utils.class_order(boxes, categories)

        get_file_name = os.path.basename(file_path).split('/')[-1]
        get_folder_name_user = get_file_name.split('.')[0]

        SAVE_DIR_USER = os.path.join(GLB_SAVE_DIR, f"{get_folder_name_user}")
        FIELDS_DETECTED = []

        if not os.path.isdir(GLB_SAVE_DIR):
            os.mkdir(GLB_SAVE_DIR)

        if not os.path.isdir(SAVE_DIR_USER):
            os.mkdir(SAVE_DIR_USER)
        else:
            for f in os.listdir(SAVE_DIR_USER):
                os.remove(os.path.join(SAVE_DIR_USER, f))

        isCccdChip = False
        imageQrCode = cv2.cvtColor(cv2.imread(file_path), cv2.COLOR_BGR2RGB)
        checkQr = glb_qreader.detect(image=imageQrCode)

        if checkQr is not None and len(checkQr) > 0:
            isCccdChip = True

        if len(categories) < 10:
            return None

        if isCccdChip:
            for index, box in enumerate(boxes):
                left, top, right, bottom = box
                if 5 < index < 9:
                    right = right + 100
                cropped_image = aligned.crop((left, top, right, bottom))
                cropped_image.save(os.path.join(SAVE_DIR_USER, f"{index}.jpg"))

            try:
                for idx, img_crop in enumerate(sorted(os.listdir(SAVE_DIR_USER))):
                    if idx > 0:
                        img_ = Image.open(os.path.join(SAVE_DIR_USER, img_crop))
                        s = glb_detector.predict(img_)
                        FIELDS_DETECTED.append(s)

                if 7 in categories:
                    FIELDS_DETECTED = (
                            FIELDS_DETECTED[:6]
                            + [FIELDS_DETECTED[6] + ", " + FIELDS_DETECTED[7]]
                            + [FIELDS_DETECTED[8]]
                    )
            except Exception as ex:
                print("Loi me no roi cccd chip: ", ex)
        else:
            for index, box in enumerate(boxes):
                left, top, right, bottom = box

                if index == 1:
                    left = left - 20
                if index == 6:
                    left = left - 20

                cropped_image = aligned.crop((left, top, right, bottom))
                cropped_image.save(os.path.join(SAVE_DIR_USER, f"{index}.jpg"))

            try:
                for idx, img_crop in enumerate(sorted(os.listdir(SAVE_DIR_USER))):
                    if idx > 0:
                        img_ = Image.open(os.path.join(SAVE_DIR_USER, img_crop))
                        s = glb_detector.predict(img_)
                        FIELDS_DETECTED.append(s)

                if len(FIELDS_DETECTED) == 9:
                    FIELDS_DETECTED_NO_CHIP = [
                        FIELDS_DETECTED[0],
                        FIELDS_DETECTED[1],
                        FIELDS_DETECTED[2],
                        FIELDS_DETECTED[3],
                        FIELDS_DETECTED[4],
                        FIELDS_DETECTED[6],
                        FIELDS_DETECTED[5] + ', ' + FIELDS_DETECTED[7],
                        FIELDS_DETECTED[8]
                    ]

                    FIELDS_DETECTED = FIELDS_DETECTED_NO_CHIP

                elif len(FIELDS_DETECTED) == 10:
                    FIELDS_DETECTED_NO_CHIP = [
                        FIELDS_DETECTED[0],
                        FIELDS_DETECTED[2],
                        FIELDS_DETECTED[3],
                        FIELDS_DETECTED[4],
                        FIELDS_DETECTED[5],
                        FIELDS_DETECTED[7] + ', ' + FIELDS_DETECTED[8],
                        FIELDS_DETECTED[6] + ', ' + FIELDS_DETECTED[9],
                        FIELDS_DETECTED[1]
                    ]

                    FIELDS_DETECTED = FIELDS_DETECTED_NO_CHIP

            except Exception as ex:
                print("Loi me no roi cccd no chip: ", ex)

        if len(FIELDS_DETECTED) == 8:
            data_final = {
                'id': FIELDS_DETECTED[0],
                'name': FIELDS_DETECTED[1],
                'dob': FIELDS_DETECTED[2],
                'sex': FIELDS_DETECTED[3],
                'nation': FIELDS_DETECTED[4],
                'home': FIELDS_DETECTED[5],
                'address': FIELDS_DETECTED[6],
                'doe': FIELDS_DETECTED[7]
            }

    except Exception as ex:
        print("Loi me no roi cccd boxes: ", ex)

    return data_final