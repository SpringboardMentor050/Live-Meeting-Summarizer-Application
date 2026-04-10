#  Live Meeting Summarizer Engine

An end-to-end, real-time meeting intelligence platform. This application captures live audio, transcribes it using offline STT, diarizes speakers, and generates structured AI summaries—all delivered through a  Streamlit dashboard with a robust SQLite backend.

##  Key Features
- **Real-Time Transcription**: Offline STT using Vosk for low-latency live feedback.
- **Speaker Diarization**: Multi-speaker identification using Pyannote.audio.
- **AI-Powered Summaries**: High-speed summarization via Groq (LLaMA 3.3).
- **Persistent Storage**: All user data and meeting histories are stored in a centralized **SQLite Database**.
- **One-Click Export**: Download reports as Markdown or professional PDFs.
- **Global Email Delivery**: Send meeting minutes to any recipient via a configured SMTP service.
- **Secure Access**: Integrated Login/Signup system with password hashing.

---

##  File-by-File Guide
| File | Purpose |

| **`app.py`** | The main Entry Point. Handles the Streamlit UI, live loops, and page routing. |
| **`auth.py`** | Manages User Authentication, SQLite schema initialization, and password security. |
| **`history_manager.py`** | Handles saving/loading meeting records to/from the SQLite `meetings` table. |
| **`milestone3_fusion.py`** | The "Processing Core." Coordinates live mic capture and real-time STT buffering. |
| **`milestone2_engine.py`** | The "Logic Hub." Contains the logic for syncing diarization timestamps with text. |
| **`module3_diarization.py`** | Interfaces with HuggingFace to perform speaker segmentation on the audio. |
| **`module4_summarization.py`** | Interfaces with Groq to transform raw transcripts into structured summaries. |
| **`export_utils.py`** | Handles PDF generation and SMTP email delivery logic. |
| **`migrate.py`** | A utility script used to transition legacy JSON data into the new SQLite database. |

---

## 🛠️ Setup & Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/Live-Meeting-Summarizer.git
   cd Live-Meeting-Summarizer
   ```

2. **Setup Virtual Environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**:
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_key_here
   HF_TOKEN=your_token_here
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_gmail_app_password
   ```

5. **Run the App**:
   ```bash
   streamlit run app.py
   ```
   *Default Admin login:* `admin` / `admin123`

---

##  Architecture Summary
The system follows a **Threaded Pipeline Architecture**:
1. **Input Layer**: `sounddevice` captures mic audio into a thread-safe Queue.
2. **STT Layer**: `Vosk` (Offline) processes audio chunks for live UI rendering.
3. **Diarization Layer**: `Pyannote` segments the saved WAV file into speaker-specific blocks.
4. **LLM Layer**: `Groq` generates the final summary from the synced transcript.
5. **Persistence Layer**: `SQLite3` stores all meeting deliverables and user profiles.

---
##  License
MIT License

Copyright (c) 2026 Mohith Naidu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


