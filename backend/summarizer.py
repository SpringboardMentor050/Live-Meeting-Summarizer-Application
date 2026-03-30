from groq import Groq

import os

def summarize_text(text):
    try:
        from groq import Groq   # lazy import (important)

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return " GROQ_API_KEY not set"

        if not text or len(text.strip()) < 10:
            return "Not enough content to summarize"

        client = Groq(api_key=api_key)

        prompt = f"""
You are an AI meeting assistant.

Summarize the following meeting transcript:

{text}

Give:
- Key Points
- Decisions
- Action Items
- Final Summary
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        return f" Groq Error: {str(e)}"