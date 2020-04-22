import pytesseract
import cv2
import datetime

pytesseract.pytesseract.tesseract_cmd = 'D:\\git\\instabot\\Tesseract-OCR\\tesseract.exe'

st_time = datetime.datetime.now()
img = cv2.imread('sample.jpg')
# img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    # cv2.imshow(key_name, img)
    # cv2.waitKey(1)
# cv2.imshow('window', img)
# name = pytesseract.image_to_string(img, lang='eng', config=" --psm 7 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRXYZ")
name = pytesseract.image_to_string(img, lang='eng', config=" --psm 7")
print(name)
ed_time = datetime.datetime.now()
diff = ed_time - st_time
print(diff)


cv2.waitKey(0)



