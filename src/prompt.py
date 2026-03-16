GENERAL_MEETING_PROMPT = """
You are an AI assistant that summarizes professional meetings.

Analyze the meeting transcript and generate a structured summary.

Transcript:
{transcript}

Return the summary in the following format:

Meeting Summary

Key Discussion Points:
- bullet points describing the main topics discussed

Decisions Made:
- list important decisions agreed during the meeting

Action Items:
- list tasks assigned to participants with responsible role if mentioned

Keep the summary concise and factual.
"""


DECISION_PROMPT = """
You are an AI assistant specialized in meeting analysis.

Extract ONLY the decisions made during the meeting.

Transcript:
{transcript}

Return the output as:

Decisions:
- decision 1
- decision 2
- decision 3

Only include confirmed decisions, not suggestions.
"""


ACTION_ITEMS_PROMPT = """
You are an AI assistant that extracts tasks from meeting transcripts.

Analyze the transcript and identify all action items.

Transcript:
{transcript}

Return the output in this format:

Action Items:
- Task description — responsible person/team if mentioned
- Task description — responsible person/team if mentioned

Only include clear tasks assigned during the meeting.
"""
KEY_POINTS_PROMPT = """
Extract the main discussion topics from the meeting transcript.

Transcript:
{transcript}

Return:

Key Discussion Points:
- topic 1
- topic 2
- topic 3
"""