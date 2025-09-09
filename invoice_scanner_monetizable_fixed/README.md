# Invoice / Receipt Scanner (Fixed - UI + Templates Added)

This refactor fixes missing core templates and adds a simple upload UI that posts to /scan/upload and shows parsed results.
Run locally:
1. Install system deps (tesseract, poppler)
2. python3 -m venv venv && source venv/bin/activate
3. pip install -r requirements.txt
4. python run.py
Open http://localhost:8080
