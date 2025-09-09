import re, json
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

def ocr_from_image(path_or_img):
    if hasattr(path_or_img, "read"):
        img = Image.open(path_or_img)
    else:
        img = Image.open(path_or_img)
    text = pytesseract.image_to_string(img)
    return text

def ocr_from_pdf(path):
    pages = convert_from_path(path, dpi=200, first_page=1, last_page=3)
    text = ""
    for p in pages:
        text += pytesseract.image_to_string(p) + "\n"
    return text

def parse_invoice_text(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    vendor = lines[0] if lines else ""
    date_regex = r"(\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b)|(?:\b\d{4}-\d{2}-\d{2}\b)"
    date_match = re.search(date_regex, text)
    date = date_match.group(0) if date_match else ""
    amt_regex = r"(?:total|amount|balance)[^\d\n\r]*([£$€]?\s*[0-9\,]+\.?[0-9]{0,2})"
    m = re.search(amt_regex, text, flags=re.IGNORECASE)
    total = m.group(1) if m else ""
    return {"vendor": vendor, "date": date, "total": total}
