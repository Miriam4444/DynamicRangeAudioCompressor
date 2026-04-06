import numpy as np
import soundfile as sf
from AudioFile import AudioFile
from Threshold import Threshold
from AudioVisualizer import AudioVisualizer

def main():
    audio = AudioFile("trimmed.wav")
    t = Threshold(audio.db)

    compressed_db = t.clippingNoKnee()

    linear = np.sign(audio.source) * (10 ** (compressed_db / 20))

    sf.write("output.wav", linear, audio.sr)
    print("done")

    vizInput = AudioVisualizer("trimmed.wav")
    vizInput.plot()

    vizOutput= AudioVisualizer("output.wav")
    vizOutput.plot()

if __name__ == "__main__":
    main()