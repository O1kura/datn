import os
import string
from io import BytesIO
from pathlib import Path

import cv2
import pytesseract
import numpy as np

from config import tesseract_OCR

# Step 1: Load the image

# Thiết lập đường dẫn của Tesseract OCR engine (đặt đúng đường dẫn của bạn)
pytesseract.pytesseract.tesseract_cmd = tesseract_OCR


# Đường dẫn đến ảnh bạn muốn xử lý


def get_file_content(image_file):
    image_bytes = BytesIO()
    image_file.save(image_bytes, format='jpeg')
    image_bytes.seek(0)
    return image_bytes


def check_string(s):
    if any(c.isalpha() or c.isdigit() for c in s):
        return True
    return False


def text_line_extraction(image, get_image=False):
    # image = cv2.imread(image_path)

    # Check if the image is None
    if image is None:
        raise ValueError("Invalid image file or path.")

    # Step 2: Preprocess the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # selected a kernel with more width so that we want to connect lines
    kernel_size = (5, 5)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)

    # Step 3: Perform the closing operation: Dilate and then close
    bw_closed = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)

    # Find contours for each text line
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    dilate = cv2.dilate(thresh, kernel, iterations=3)

    contours = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    # Filter contours to select those whose width is at least 3 times its height
    # filtered_contours = [cnt for cnt in contours if (cv2.boundingRect(cnt)[2] / cv2.boundingRect(cnt)[3])>=3.0]

    # Sort contours based on y-coordinate
    sorted_contours = sorted(contours, key=lambda contour: cv2.boundingRect(contour)[1])
    # sorted_contours = sorted(contours, key=lambda contour: cv2.boundingRect(contour)[1])
    # print(len(sorted_contours))
    # Step 4: Recognize text lines
    uppercase_letters = list(string.ascii_uppercase)
    padding = 1

    result = []

    for contour in sorted_contours:
        # for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        x, y, w, h = (x - padding, y - padding, w + padding, h + padding)
        # print("x", x)
        # print("y", y)
        # print("w", w)
        # print("h", h)

        # Recognize each line. Crop the image for each line and pass to OCR engine.
        line_image = image[y:y + h, x:x + w]
        line_text = pytesseract.image_to_string(line_image)
        if (line_text.strip() != ''):
            # Draw rectangle around each line, thickness=-1 -> filled rectangle
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 255), -1)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Tính toán vị trí để viết chữ vào giữa hình chữ nhật
            text = uppercase_letters.pop(0)
            text_font = cv2.FONT_HERSHEY_SIMPLEX

            text_width, text_height = cv2.getTextSize(text, text_font, 1, 2)[0]
            text_scale = min(w / text_width, h / text_height) * 0.8
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
                "box": {
                    "x": x,
                    "y": y,
                    "rect_x": x + w,
                    "rect_y": y + h,
                    "filled_color": (255, 255, 255),
                    "border_color": (0, 255, 0),
                    "border_thickness": 2,
                },
                "scale": text_scale,
                "thickness": text_thickness,
                "symbol_text": {
                    "text_x": text_x,
                    "text_y": text_y,
                    "text_scale": text_scale,
                    "text_font": text_font,
                    "color": (255, 0, 0),
                    "text_thickness": text_thickness
                }
                # "output_path": output_path
            }
            result.append(dict)

            # Viết chữ vào chính giữa hình chữ nhật
            # cv2.putText(image, text, (text_x, text_y), text_font, text_scale, (255,182,193), text_thickness)
            if get_image:
                cv2.putText(image, text, (text_x, text_y), text_font, text_scale, (255, 0, 0), text_thickness)

    # cv2.imwrite(output_path, image)
    if get_image:
        return result, image

    return result


def text_line_extraction_2(image, get_image=False):
    # image = cv2.imread(image_path)
    # Check if the image is None
    if image is None:
        raise ValueError("Invalid image file or path.")

    # Step 2: Preprocess the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # blur = cv2.GaussianBlur(gray, (3, 3), 0)
    # bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Extract only using pytesseract
    print(pytesseract.image_to_data(gray))
    results = pytesseract.image_to_data(gray, output_type='dict')

    # block_words_count = {}
    true_text = []
    #
    # for i in range(0, len(results["text"])):
    #     text = results["text"][i]
    #     conf = int(results["conf"][i])
    #     block_num = results["block_num"][i]
    #     # filter out weak confidence text localizations
    #     # combine text from block_text to a string and get the bounds of that block_text
    #     if conf > 80 and text.strip() != '':
    #         if block_num in block_words_count:
    #             block_words_count[block_num] = block_words_count[block_num] + 1
    #         else:
    #             block_words_count[block_num] = 1

    dict_res = {}
    # loop over each of the individual text localizations
    for i in range(0, len(results["text"])):
        # extract the bounding box coordinates of the text region from
        # the current result
        x = results["left"][i]
        y = results["top"][i]
        w = results["width"][i]
        h = results["height"][i]
        # extract the OCR text itself along with the confidence of the
        # text localization
        block_num = results["block_num"][i]
        line = results["line_num"][i]
        text = results["text"][i]
        conf = int(results["conf"][i])
        # filter out weak confidence text localizations
        # combine text from block_text to a string and get the bounds of that block_text
        if conf > 66:
            # if block_words_count[block_num] > 6:
            #     true_text.append({'text': text, "x": x, "y": y, "rect_x": x + w, "rect_y": y + h})
            #     continue
            if block_num in dict_res:
                avg_text_width = (dict_res[block_num]['rect_x'] - dict_res[block_num]['x']) / len(
                    dict_res[block_num]['text'])
                avg_text_height = (dict_res[block_num]['rect_y'] - dict_res[block_num]['y']) / dict_res[block_num][
                    'line']

                if line == dict_res[block_num]['line']:
                    # If the beginning of the next word is close to the last word, append to the last word
                    if (x - dict_res[block_num]["rect_x"] > 1.6 * avg_text_width
                            or y + h - dict_res[block_num]["rect_y"] > 1.6 * avg_text_height):
                        true_text.append(dict_res[block_num])
                        dict_res[block_num] = {'text': text, "x": x, "y": y, "rect_x": x + w, "rect_y": y + h,
                                               "component": [i], "line": line}
                        continue

                    dict_res[block_num]['text'] = dict_res[block_num]['text'] + ' ' + text
                    dict_res[block_num]["x"] = min(dict_res[block_num]["x"], x)
                    dict_res[block_num]["y"] = min(dict_res[block_num]["y"], y)
                    dict_res[block_num]["rect_x"] = max(dict_res[block_num]["rect_x"], x + w)
                    dict_res[block_num]["rect_y"] = max(dict_res[block_num]["rect_y"], y + h)
                    dict_res[block_num]["component"].append(i)
                    dict_res[block_num]["line"] = line
                else:
                    # If the centers not match
                    if ((abs((2 * x + w) / 2 - (
                            dict_res[block_num]["rect_x"] + dict_res[block_num]['x']) / 2) > 1.6 * avg_text_width
                         # Or the beginning of the new line does not match the beginning of the current block:
                         and abs(x - dict_res[block_num]["x"]) > 1.6 * avg_text_width)
                            or y + h - dict_res[block_num]["rect_y"] > 1.6 * avg_text_height):
                        true_text.append(dict_res[block_num])
                        dict_res[block_num] = {'text': text, "x": x, "y": y, "rect_x": x + w, "rect_y": y + h,
                                               "component": [i], "line": line}
                        continue

                    dict_res[block_num]['text'] = dict_res[block_num]['text'] + ' ' + text
                    dict_res[block_num]["x"] = min(dict_res[block_num]["x"], x)
                    dict_res[block_num]["y"] = min(dict_res[block_num]["y"], y)
                    dict_res[block_num]["rect_x"] = max(dict_res[block_num]["rect_x"], x + w)
                    dict_res[block_num]["rect_y"] = max(dict_res[block_num]["rect_y"], y + h)
                    dict_res[block_num]["component"].append(i)
                    dict_res[block_num]["line"] = line
            else:
                dict_res[block_num] = {'text': text, "x": x, "y": y, "rect_x": x + w, "rect_y": y + h, "component": [i],
                                       "line": line}
    true_text.extend(dict_res.values())
    result = []

    # Loop through the block_text in dict_res calculated above
    # for formatting response data and write to image if necessary
    padding = 1
    for block_text in true_text:
        if check_string(block_text["text"]):
            word_count = len(block_text["text"].split())
            if word_count > 7:
                for i in block_text['component']:
                    x = results["left"][i]
                    y = results["top"][i]
                    w = results["width"][i]
                    h = results["height"][i]
                    text = results["text"][i]
                    if check_string(text):
                        _block_text = {'text': text, "x": x, "y": y, "rect_x": x + w, "rect_y": y + h}
                        dict = format_box_text_to_dict(_block_text, 1)
                        result.append(dict)

                        # Draw rectangle around each line, thickness=-1 -> filled rectangle
                        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 255), -1)
                        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                        if get_image:
                            cv2.putText(image, dict["symbol"], (dict["text_x"], dict["text_y"]),
                                        dict['symbol_text']["text_font"], dict['scale'], dict['symbol_text']["color"],
                                        dict['thickness'])
                continue
            x = block_text['x'] - padding
            y = block_text['y'] - padding
            w = block_text['rect_x'] - x + padding
            h = block_text['rect_y'] - y + padding
            # Draw rectangle around each line, thickness=-1 -> filled rectangle
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 255), -1)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Tính toán vị trí để viết chữ vào giữa hình chữ nhật
            dict = format_box_text_to_dict(block_text, 1)
            result.append(dict)

            # Viết chữ vào chính giữa hình chữ nhật
            if get_image:
                cv2.putText(image, dict["symbol"], (dict["text_x"], dict["text_y"]), dict['symbol_text']["text_font"],
                            dict['scale'], dict['symbol_text']["color"], dict['thickness'])

    if get_image:
        return result, image

    return result


def format_box_text_to_dict(block_text, padding):
    x = block_text['x'] - padding
    y = block_text['y'] - padding
    w = block_text['rect_x'] - x + padding
    h = block_text['rect_y'] - y + padding

    text = block_text['text']
    text_font = cv2.FONT_HERSHEY_SIMPLEX

    text_width, text_height = cv2.getTextSize(text, text_font, 1, 2)[0]
    text_scale = min(w / text_width, h / text_height) * 0.8
    text_thickness = 1

    text_size = cv2.getTextSize(text, text_font, text_scale, text_thickness)[0]
    text_width, text_height = text_size[0], text_size[1]
    text_x = int((w - text_width) / 2) + x
    text_y = int((h + text_height) / 2) + y

    dict = {
        "symbol": text,
        "text": block_text['text'],
        "x": x,
        "y": y,
        "text_x": text_x,
        "text_y": text_y,
        "w": text_width,
        "h": text_height,
        "box": {
            "x": x,
            "y": y,
            "rect_x": x + w,
            "rect_y": y + h,
            "filled_color": (255, 255, 255),
            "border_color": (0, 255, 0),
            "border_thickness": 2,
        },
        "scale": text_scale,
        "thickness": text_thickness,
        "symbol_text": {
            "text_x": text_x,
            "text_y": text_y,
            "text_scale": text_scale,
            "text_font": text_font,
            "color": (255, 0, 0),
            "text_thickness": text_thickness
        }
    }
    return dict
