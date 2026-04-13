# 🎙️ Live Meeting Engine AI - Demo Script

Use this step-by-step guide to perform a flawless presentation of the 'Live Meeting Summarizer' application.

---

## 🛠️ Phase 1: Preparation (Before the Demo)
1. **Check API Keys**: Ensure your `.env` file has your `GROQ_API_KEY`, `HF_TOKEN`, and `SENDER_EMAIL` / `SENDER_PASSWORD` (App Password).
2. **Audio Setup**: Ensure your microphone is connected and working.
3. **Reset Database**: (Optional) You can start fresh or use existing session data in `app_data.db`.
4. **Launch Application**:
   ```bash
   streamlit run app.py
   ```

---

## 🏁 Phase 2: Introduction & Authentication (3 Minutes)
1. **The Vision**: Start by explaining: *"Traditional meetings are often lost—notes are messy, and action items are forgotten. Our solution captures the meeting's intelligence in real-time."*
2. **The Login**:
   - Point out the **sleek, card-based login**.
   - Show the **"Create Account"** feature to demonstrate the SQLite-powered persistence.
   - Log in using `admin` / `admin123`.

---

## 🔴 Phase 3: The Live Experience (5 Minutes)
1. **Dashboard Overview**: Explain the "Control Center" vs. the "Live Feed."
2. **The Start**: Click **"🔴 Start Live Recording."**
3. **Live Feedback**: Start talking (as if you're in a real meeting). 
   - *Key Point to Say:* *"Notice how as I speak, the transcription appears instantly on the right. This is powered by an offline STT model, ensuring privacy and speed."*
4. **The Stop**: Click **"⏹️ Stop & Generate Report."**
   - *Key Point to Say:* *"Once stopped, the system kicks off its backend 'Fusion Engine'—it's now identifying speakers and summarizing the entire transcript through the Groq LLaMA 3.3 model."*

---

## 🧠 Phase 4: Summarization & Export (5 Minutes)
1. **Report Breakdown**: Show the **AI Summary**. 
   - Point out the Markdown formatting (headings, icons, bullet points).
   - Show the **Diarized Transcript** (e.g., *Speaker 0 / Speaker 1*).
2. **One-Click Delivery**:
   - Click **"📥 Export PDF"**. Open the generated `summary.pdf` in VS Code or a browser. Explain how the automatic PDF generation saves time.
   - **The Email Test**: Enter a recipient's email in the form and click **"Send Summary."** Demonstrate the success message. *"I can instantly share these minutes with any stakeholder with one click."*

---

## 📜 Phase 5: Session History (2 Minutes)
1. **History Tab**: Click on **"📁 Session History."**
2. **Persistence Demo**: Show past meetings saved in the SQLite database.
   - *Key Point to Say:* *"Every meeting is stored safely. I can always come back and download the transcript or summary from weeks ago."*

---

## 🏁 Phase 6: Conclusion (1 Minute)
1. **Summary of Tech Stack**: Mentions **Vosk (STT)**, **Pyannote (Diarization)**, **Groq (AI)**, and **SQLite (Storage)**.
2. **Closing Statement**: *"The Meeting Engine AI transforms the way teams collaborate—turning raw conversations into structured, actionable intelligence instantly. Thank you!"*

---
*Prepared by the Antigravity AI Assistant for the Final Milestone 3 Presentation.*
