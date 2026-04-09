import sounddevice as sd
import numpy as np

DEVICE_INDEX = 9
SAMPLE_RATE = 48000
DURATION = 5

print("Recording 5 seconds... Speak loudly!")

recording = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    device=DEVICE_INDEX,
    dtype='float32'
)

sd.wait()

print("Recording finished.")
print("Max amplitude:", np.max(recording))
print("Min amplitude:", np.min(recording))
