from pyannote.metrics.diarization import DiarizationErrorRate
from pyannote.database.util import load_rttm

# -----------------------------
# FILE PATHS
# -----------------------------

REFERENCE_RTTM = "diarization/reference_realtime.rttm"
PREDICTED_RTTM = "diarization/predicted_realtime.rttm"

# -----------------------------
# LOAD RTTM FILES
# -----------------------------

reference = load_rttm(REFERENCE_RTTM)
hypothesis = load_rttm(PREDICTED_RTTM)

# -----------------------------
# INITIALIZE DER METRIC
# -----------------------------

metric = DiarizationErrorRate()

# -----------------------------
# COMPUTE DER
# -----------------------------

for uri in reference:

    if uri in hypothesis:

        metric(reference[uri], hypothesis[uri])

    else:

        print(f"{uri} not found in predicted RTTM")

# -----------------------------
# PRINT RESULT
# -----------------------------

print("\nRealtime Diarization Error Rate (DER):\n")
print(metric)