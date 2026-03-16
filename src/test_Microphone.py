import sounddevice as sd
import soundfile as sf
import numpy as np

samplerate = 48000
duration = 5

print(" Recording will start in 2 seconds...")
sd.sleep(2000)

print("Recording... Speak now")

audio = sd.rec(
    int(duration * samplerate),
    samplerate=samplerate,
    channels=2,
    dtype="float32"
)

sd.wait()

# convert stereo → mono
audio = np.mean(audio, axis=1)

# normalize audio
audio = audio / np.max(np.abs(audio))

# amplify signal
audio = audio * 3

print("Max audio level:", np.max(np.abs(audio)))

sf.write("mic_test.wav", audio, samplerate)

print("✅ Recording finished")
print("Saved file: mic_test.wav")