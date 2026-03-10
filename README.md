# AI Live Meeting Summarizer

This project converts meeting audio into text, identifies speakers, and generates a summary.

## Features
- Speech to Text using Whisper
- Speaker Diarization using Pyannote
- Meeting Summary Generation
- Word Error Rate (WER) Evaluation

## Technologies Used
- Python
- Streamlit
- OpenAI Whisper
- Pyannote.audio
- HuggingFace

## How to Run

Install dependencies:

pip install -r requirements.txt

Run the application:

streamlit run app.py

## Project Structure

app.py – Main Streamlit application  
stt.py – Speech to text using Whisper  
diarization.py – Speaker diarization  
summarizer.py – Text summarization  
utils.py – Helper functions  

## Author
Jampina Nagalakshmi
