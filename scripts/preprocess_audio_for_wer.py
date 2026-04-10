"""
Preprocess audio: apply noise reduction and remove silence.
"""
import librosa
import soundfile as sf
import numpy as np

input_path = "data/processed/clean_30s.wav"
output_path = "data/processed/clean_30s.wav"

# Load audio
y, sr = librosa.load(input_path, sr=16000)

# 1. Apply noise reduction using spectral gating
# Estimate noise from the quietest frames
frame_length = 2048
hop_length = 512
S = librosa.stft(y, n_fft=frame_length, hop_length=hop_length)
S_mag = np.abs(S)

# Compute noise floor as the 10th percentile of magnitude across time
noise_floor = np.percentile(S_mag, 10, axis=1, keepdims=True)

# Gate: keep only frames above the noise floor (with margin)
gate = S_mag > (noise_floor * 1.5)
S_gated = S * gate

# Reconstruct
y_denoised = librosa.istft(S_gated, hop_length=hop_length, length=len(y))

# 2. Apply voice activity detection (VAD) to remove silence
# Use energy-based VAD: trim frames below threshold
S_energy = librosa.feature.melspectrogram(y=y_denoised, sr=sr, n_mels=40)
energy = np.mean(S_energy, axis=0)
energy_db = librosa.power_to_db(energy, ref=np.max(energy))

# Threshold: keep frames above -40 dB
vad_threshold = -40
vad_mask = energy_db > vad_threshold

# Convert VAD mask from frames back to samples
vad_mask_samples = np.repeat(vad_mask, hop_length)[:len(y_denoised)]

# Trim leading/trailing silence by finding start and end indices
nonsilent_idx = np.where(vad_mask_samples)[0]
if len(nonsilent_idx) > 0:
    start, end = nonsilent_idx[0], nonsilent_idx[-1] + 1
    y_trimmed = y_denoised[start:end]
else:
    y_trimmed = y_denoised

# Save preprocessed audio
sf.write(output_path, y_trimmed, sr)
print(f"Preprocessed audio saved to {output_path}")
print(f"Original length: {len(y)/sr:.2f}s, Preprocessed length: {len(y_trimmed)/sr:.2f}s")
