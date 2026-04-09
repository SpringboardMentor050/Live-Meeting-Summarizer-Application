GENERAL_MEETING_PROMPT = """
You are an AI assistant that summarizes meetings.

Summarize the following meeting transcript.

Transcript:
{transcript}

Provide:
1. Key discussion points
2. Important decisions
3. Action items
"""

DECISION_PROMPT = """
Extract the key decisions from the meeting transcript.

Transcript:
{transcript}

Provide a list of decisions made during the meeting.
"""

ACTION_ITEMS_PROMPT = """
Extract action items from the meeting transcript.

Transcript:
{transcript}

List all tasks assigned to participants.
"""