from groq import Groq

client = Groq(api_key="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")

def generate_summary(text):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # ✅ WORKING MODEL
            messages=[
                {"role": "user", "content": f"Summarize this meeting:\n{text}"}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {e}"