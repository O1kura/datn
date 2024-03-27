import os
import string
from io import BytesIO
from pathlib import Path

import cv2
import pytesseract
import numpy as np
# Step 1: Load the image

# Thiết lập đường dẫn của Tesseract OCR engine (đặt đúng đường dẫn của bạn)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# Đường dẫn đến ảnh bạn muốn xử lý


def get_file_content(image_file):
    image_bytes = BytesIO()
    image_file.save(image_bytes, format='jpeg')
    image_bytes.seek(0)
    return image_bytes


def text_line_extraction(image):
    # image = cv2.imread(image_path)

    # Check if the image is None
    if image is None:
        raise ValueError("Invalid image file or path.")

    # Step 2: Preprocess the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # selected a kernel with more width so that we want to connect lines
    kernel_size = (5,5)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)

    # Step 3: Perform the closing operation: Dilate and then close
    bw_closed = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)

    # Find contours for each text line
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    dilate = cv2.dilate(thresh, kernel, iterations=3)

    contours = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    # Filter contours to select those whose width is at least 3 times its height
    filtered_contours = [cnt for cnt in contours if (cv2.boundingRect(cnt)[2] / cv2.boundingRect(cnt)[3])>=3.0]

    # Sort contours based on y-coordinate
    sorted_contours = sorted(filtered_contours, key=lambda contour: cv2.boundingRect(contour)[1])
    # print(len(sorted_contours))
    # Step 4: Recognize text lines
    uppercase_letters = list(string.ascii_uppercase)
    padding=1

    result = []

    for contour in sorted_contours:
    # for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        x, y, w, h = (x-padding, y-padding, w+padding, h+padding) 
        # print("x", x)
        # print("y", y)
        # print("w", w)
        # print("h", h)

        # Recognize each line. Crop the image for each line and pass to OCR engine.
        line_image = image[y:y + h, x:x+w]
        line_text = pytesseract.image_to_string(line_image)
        print(line_text)
        if (line_text.strip() != ''):
            # Draw rectangle around each line, thickness=-1 -> filled rectangle
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 255), -1)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Tính toán vị trí để viết chữ vào giữa hình chữ nhật
            text = uppercase_letters.pop(0)
            text_font = cv2.FONT_HERSHEY_SIMPLEX

            text_width, text_height = cv2.getTextSize(text, text_font, 1, 2)[0]
            text_scale = min(w / text_width,h / text_height) * 0.8
            text_thickness = 1

            text_size = cv2.getTextSize(text, text_font, text_scale, text_thickness)[0]
            text_width, text_height = text_size[0], text_size[1]
            text_x = int((w - text_width) / 2) + x
            text_y = int((h + text_height) / 2) + y

            dict = {
                "symbol": text,
                "text": line_text,
                "x": x,
                "y": y,
                "text_x": text_x,
                "text_y": text_y,
                "w": text_width,
                "h": text_height,
                "scale": text_scale,
                "thickness": text_thickness,
                # "output_path": output_path
            }
            result.append(dict)
            
            # Viết chữ vào chính giữa hình chữ nhật
            # cv2.putText(image, text, (text_x, text_y), text_font, text_scale, (255,182,193), text_thickness)
            cv2.putText(image, text, (text_x, text_y), text_font, text_scale, (255,0,0), text_thickness)

    # cv2.imwrite(output_path, image)
    return result, image

# res = text_line_extraction(r'C:\Users\viet6\Downloads\image.png','C:\\Users\\viet6\\OneDrive\\Pictures\\Screenshots\\results.png')
# print(res)