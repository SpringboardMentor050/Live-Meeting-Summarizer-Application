# Video Demo Script - Live Meeting Analyzer
**Target length**: 3-5 minutes

## Part 1: Introduction & Login (0:00 - 0:30)
*   **Start** on the login screen.
*   **Script**: "Welcome to my Live Meeting Analyzer demo. This is a complete, real-time transcription, diarization, and summarization engine built entirely in Python. First, let's log in securely via the authenticated gateway using our demo credentials."
*   **Action**: Type `admin` and `admin123`. Click "Sign In".

## Part 2: The UI & Configuration (0:30 - 1:00)
*   **Script**: "Once inside, you're greeted by a premium control dashboard. On the left sidebar, we establish secure API connections to Hugging Face for speaker separation and Groq LLaMA for summarization. The main view gives us a control center and our live feed."

## Part 3: Live Recording Demo (1:00 - 2:00)
*   **Action**: Click `🔴 Start Live Recording`.
*   **Script**: "As I talk, the multi-threaded backend captures my microphone using `sounddevice` and passes it instantly to an offline Vosk Speech-to-Text model. You can see the transcription rendering on-the-fly right here in the terminal feed. Let's imagine I say: 'Hi everyone, in today's sync we need to prioritize fixing the UI bugs and shipping the email feature by Friday. Are we all agreed?'"
*   **Action**: Speak dynamically to populate the live feed.

## Part 4: Post-Processing & Insights (2:00 - 3:00)
*   **Action**: Click `⏹️ Stop & Generate Report`.
*   **Script**: "When I hit stop, the tool switches to post-processing. It's now mapping the audio to distinct speakers using `pyannote` and sending the formatted dialogue to the Groq API."
*   **Action**: Wait for the "Report Generated" status. Show the `👥 Diarized Transcript`.
*   **Script**: "As you can see, the exact words are now paired with speaker labels."
*   **Action**: Switch to the `📓 AI Summary & Action Items` tab.
*   **Script**: "The AI has automatically analyzed our sync, producing executive highlights and isolating actionable tasks."

## Part 5: History, Export, and Email (3:00 - 4:00)
*   **Script**: "But it doesn't just display it—it saves it."
*   **Action**: Navigate to the `📁 Session History` tab. Open the newly logged meeting.
*   **Script**: "All sessions are securely logged to a JSON backend. Let's say I want to share this with my project manager. I can export it instantly as a Markdown file, generate a PDF report automatically... or simply send it directly via the integrated SMTP email module."
*   **Action**: Fill out the email field and hit Send.
*   **Script**: "Thank you for watching."
