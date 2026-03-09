from pyannote.metrics.diarization import DiarizationErrorRate
from pyannote.database.util import load_rttm

# Paths
reference_file = "diarization/reference.rttm"
predicted_file = "diarization/predicted.rttm"

# Load RTTM files
reference = load_rttm(reference_file)
hypothesis = load_rttm(predicted_file)

# Initialize DER metric
metric = DiarizationErrorRate()

# Compute DER
for uri in reference:
    if uri in hypothesis:
        metric(reference[uri], hypothesis[uri])
    else:
        print(f"{uri} not found in predicted file")

# Print final DER
print("\nDiarization Error Rate (DER):")
print(metric)