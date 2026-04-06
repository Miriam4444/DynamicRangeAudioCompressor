import numpy as np
import matplotlib.pyplot as plt
import librosa as lib
import os

class AudioVisualizer:
    def __init__(self, file: str):
        self.source, self.sr = lib.load(file, sr=None)
        self.file = os.path.basename(file)
        self.N = len(self.source)
        self.time = np.arange(self.N) / self.sr
        self.db = 20 * np.log10(np.abs(self.source) + 1e-10)

    def computeRMS(self, frameLength=2048, hopLength=512):
        rms = lib.feature.rms(y=self.source, frame_length=frameLength, hop_length=hopLength)[0]
        rmsTime = lib.frames_to_time(np.arange(len(rms)), sr=self.sr, hop_length=hopLength)
        return rms, rmsTime

    def plot(self):
        rms, rmsTime = self.computeRMS()

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6))
        fig.suptitle(self.file)

        # dB vs time
        ax1.plot(self.time, self.db, color="steelblue", linewidth=0.5)
        ax1.axhline(y=-20, color="red", linestyle="--", linewidth=1, label="threshold")
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Amplitude (dB)")
        ax1.set_title("Decibel vs Time")
        ax1.legend()

        # RMS loudness vs time
        ax2.plot(rmsTime, rms, color="darkorange", linewidth=0.8)
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("RMS Loudness")
        ax2.set_title("RMS Loudness vs Time")

        plt.tight_layout()
        plt.show()