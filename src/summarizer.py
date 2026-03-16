from groq import Groq

client = Groq(api_key="YOUR_GROQ_API_KEY")


def summarize_meeting(transcript):

    prompt = f"""
You are an AI meeting assistant.

Summarize the meeting transcript.

Extract:
• Key discussion points
• Decisions made
• Action items

Transcript:
{transcript}

Provide a structured summary.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content