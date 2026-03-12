from summarizer import summarize_meeting

transcript = """
Speaker 1: Hello everyone welcome to today's meeting.
Speaker 2: We need to finalize the project timeline.
Speaker 1: The backend implementation is almost complete.
Speaker 2: We should set the deadline for next Friday.
Speaker 1: Agreed, testing will start tomorrow.
"""

summary = summarize_meeting(transcript)

print("\n===== MEETING SUMMARY =====\n")
print(summary)