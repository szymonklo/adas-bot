import keyboard
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def find_speed(image):
    text_speed = ocr(image)
    try:
        speed = int(text_speed)
        if speed < 170:
            return speed
        else:
            return None
    except ValueError:
        return None


def ocr(image):
    text = pytesseract.image_to_string(image, config='--oem 1 --psm 8 digits')
    # keyboard.press_and_release('esc')

    return text


"""ddd
$ tesseract --help-psm
Page segmentation modes:
  0    Orientation and script detection (OSD) only.
  1    Automatic page segmentation with OSD.
  2    Automatic page segmentation, but no OSD, or OCR.
  3    Fully automatic page segmentation, but no OSD. (Default)
  4    Assume a single column of text of variable sizes.
  5    Assume a single uniform block of vertically aligned text.
  6    Assume a single uniform block of text.
  7    Treat the image as a single text line.
  8    Treat the image as a single word.ddd
  9    Treat the image as a single word in a circle.
 10    Treat the image as a single character.
 11    Sparse text. Find as much text as possible in no particular order.
 12    Sparse text with OSD.
 13    Raw line. Treat the image as a single text line,
       bypassing hacks that are Tesseract-specific.
       
$ tesseract --help-oem
OCR Engine modes:
  0    Legacy engine only.
  1    Neural nets LSTM engine only.
  2    Legacy + LSTM engines.
  3    Default, based on what is available.
  
text_1 = pytesseract.image_to_string(image, lang='eng', config='--psm 10 digits')
ocr_result = pytesseract.image_to_string(image, lang='eng', config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
ocr_result_2 = pytesseract.image_to_string(image, lang='eng',
                                         config='--psm 10 -c tessedit_char_whitelist=0123456789')
ocr_result_3 = pytesseract.image_to_string(image, lang='eng',
                                           config='-c tessedit_char_whitelist=0123456789')  
"""