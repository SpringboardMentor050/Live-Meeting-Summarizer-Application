import sounddevice as sd
import numpy as np

class AudioRecorder:
    def __init__(self, samplerate=16000):
        self.samplerate = samplerate
        self.recording = []
        self.stream = None

    def callback(self, indata, frames, time, status):
        self.recording.append(indata.copy())

    def start_recording(self):
        self.recording = []
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=1,
            callback=self.callback
        )
        self.stream.start()

    def stop_recording(self):
        self.stream.stop()
        self.stream.close()
        audio = np.concatenate(self.recording, axis=0)
        return audio