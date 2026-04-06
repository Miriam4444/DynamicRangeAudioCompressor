import numpy as np
import matplotlib as plt
from matplotlib.colors import Normalize, ListedColormap
import librosa as lib
import scipy as sci
import statistics as stat
import os
from typing import Any

NDArray = np.ndarray[Any, np.dtype[np.float64]]

class AudioFile:
    def __init__(self, file: str):

        ##############################################
        # attributes of the audiofile object
        ##############################################

        # load wav file as array and store sample rate
        self.source, self.sr =  lib.load(file, sr=None) 

        # file name without path
        self.file: str = os.path.basename(file)

        # store number of samples in original file
        self.N: int = len(self.source)

        # store time array for original signal
        self.time: NDArray = np.arange(self.N)/self.sr
        self.lengthinseconds: float = self.N/self.sr

        # store decibel values of the original signal
        self.db: NDArray = 20 * np.log10(np.abs(self.source) + 1e-10)

        

        
        