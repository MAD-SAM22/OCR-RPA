import cv2
import pytesseract
import numpy as np
import easyocr
from PIL import Image
import google.generativeai as genai
import sys 
import os 
from dotenv import load_dotenv,dotenv_values


class EasyOcr:
    def __init__(self):
        # Ensure Tesseract is installed and available
        pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'  # Update to your local tesseract installation path if needed

        # Initialize the EasyOCR reader
        self.reader = easyocr.Reader(['en'])

    def apply_ocr(self, image_path):
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image not found: {image_path}")
        text = self.reader.readtext(image_path)
        return text

class Tesseract:
    def __init__(self ):
        # Set up Tesseract executable
        pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    
    def preprocess_image(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        filtered = cv2.bilateralFilter(gray, 9, 75, 75)
        thresh = cv2.adaptiveThreshold(filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, 31, 2)
        kernel = np.ones((1, 1), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        return opening
    
    def apply_ocr(self, image_path):
        preprocessed_image = self.preprocess_image(cv2.imread(image_path))
        pil_image = Image.fromarray(preprocessed_image)
        config = r'--oem 3 --psm 6'
        extracted_text = pytesseract.image_to_string(pil_image, config=config)
        return extracted_text
class Gemini:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.instruction = (
            """
            You are given extracted text from an invoice, extract the data and return them in the following order:
            invoice object with client name, invoice number, invoice date, due date. 
            Item purchased objects with their description, quantity, and total price.
            subtotal object with tax(if applicable), discount(if applicable), and total.
            Payment instructions with due date, bank name, account number, and payment method.
            in JSON format for direct use without any extra text. 
            additionally, dont write json before the text 
            """
        )
        self.model = genai.GenerativeModel("models/gemini-1.5-pro", system_instruction=self.instruction)

    def generate_response(self, extracted_text):
        response = self.model.generate_content(f'{extracted_text}')
        return response.text

# Example usage


image_path = rf"C:\Users\Osama hosam\Desktop\gg\OCR+FormatFilling\OCR+FormatFilling\imgs\rr.png"

api_key = os.getenv("api_key")  # Replace with your API key

# # Create an instance of Gemini
gemini_instance = Gemini(api_key)

 # Create an instance of EasyOcr
easyocr_instance = EasyOcr()

# # Apply OCR to the image
extracted_text = easyocr_instance.apply_ocr(image_path)

# # Generate response from Gemini model
response_text = gemini_instance.generate_response(extracted_text)

print(response_text)
