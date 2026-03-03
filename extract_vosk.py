import zipfile
import os

zip_path = r"f:\LiveMeetingAnalyzerProject\vosk-model-small-en-us-0.15.zip"
extract_path = r"f:\LiveMeetingAnalyzerProject"

print(f"Extracting {zip_path} to {extract_path}...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)
print("Extraction complete.")
