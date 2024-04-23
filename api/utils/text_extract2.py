# Import required packages
import cv2
import numpy as np
import pytesseract
from PIL import Image

# Mention the installed location of Tesseract-OCR in your system
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def convertPILtoOpenCVImage(image):
    pil_image = image.convert('RGB')

    # Convert the PIL image to a numpy array
    numpy_image = np.array(pil_image)

    # Change color channels from RGB to BGR
    open_cv_image = numpy_image[:, :, ::-1].copy()
    return open_cv_image


def convertOpenCVImagetoPIL(img):
    return Image.fromarray(img)


def text_extraction(img):
    # Read image from which text needs to be extracted
    # img = cv2.imread(r'C:\Users\viet6\Downloads\image.png')
    # img = cv2.imread(img)
    # Preprocessing the image starts

    # Convert the image to gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Performing OTSU threshold
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

    # Specify structure shape and kernel size.
    # Kernel size increases or decreases the area
    # of the rectangle to be detected.
    # A smaller value like (10, 10) will detect
    # each word instead of a sentence.
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))

    # Applying dilation on the threshold image
    dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)

    # Finding contours
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_NONE)

    # Creating a copy of image
    im2 = img.copy()

    # A text file is created and flushed
    # file = open("recognized.txt", "w+")
    # file.write("")
    # file.close()

    # Looping through the identified contours
    # Then rectangular part is cropped and passed on
    # to pytesseract for extracting text from it
    # Extracted text is then written into the text file
    res = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Drawing a rectangle on copied image
        rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Cropping the text block for giving input to OCR
        cropped = im2[y:y + h, x:x + w]

        # Open the file in append mode
        # file = open("recognized.txt", "a")

        # Apply OCR on the cropped image
        text = pytesseract.image_to_string(cropped)

        res.append(text)

    return res, im2
    # Appending the text into file
    # file.write(text)
    # file.write("\n")
    #
    # # Close the file
    # file.close
# text_extraction()


def text_extract(img):
    base_image = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 50))
    dilate = cv2.dilate(thresh, kernal, iterations=1)

    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if h > 200 and w > 250:
            roi = base_image[y:y + h, x:x + w]
            cv2.rectangle(img, (x, y), (x + w, y + h), (36, 255, 12), 2)

    ocr_result_original = pytesseract.image_to_string(base_image)
    print(ocr_result_original)


def text_extract_3(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 218])
    upper = np.array([157, 54, 255])
    mask = cv2.inRange(hsv, lower, upper)

    # Create horizontal kernel and dilate to connect text characters
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    dilate = cv2.dilate(mask, kernel, iterations=5)

    # Find contours and filter using aspect ratio
    # Remove non-text contours by filling in the contour
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        ar = w / float(h)
        if ar < 5:
            cv2.drawContours(dilate, [c], -1, (0, 0, 0), -1)

    # Bitwise dilated image with mask, invert, then OCR
    result = 255 - cv2.bitwise_and(dilate, mask)
    data = pytesseract.image_to_string(result, lang='eng', config='--psm 6')
    print(data)

    cv2.imshow('mask', mask)
    cv2.imshow('dilate', dilate)
    cv2.imshow('result', result)
    cv2.waitKey()
