from scipy import signal
import numpy as np
from common_utils.filter_utils import butter_bandpass_filter
from config import *
from scipy.fft import rfft, rfftfreq
from common_utils.utils import dist_to_freq
from typing import List

class Extract3D:
    def __init__(self, chirp):
        self.chirp = chirp

    def mix_operate(self, peaks: np.ndarray, record: np.ndarray) -> np.ndarray:
        """Execute the mix operation

        Args:
            peaks (np.ndarray): 1D array, segmentation of every chirp
            record (np.ndarray): 1D array, audio signal in one channel

        Returns:
            np.ndarray: mix signal after multiplication
        """
        mix_signal = []
        for i in range(len(peaks)-1):
            if peaks[i+1] - peaks[i] != CHIRP_LENGTH:
                continue
            mix_signal.extend(np.multiply(record[peaks[i]:peaks[i+1]], self.chirp[:CHIRP_LENGTH]))
        return np.array(mix_signal)

    def get_freqs_phases(self, mix_signal: np.ndarray, window=2048) -> tuple:
        """Get frequency power, phase and frequency of the mix signals

        Args:
            mix_signal (np.ndarray): shape = (1, number of samples)
            window (int, optional): window size of fft. Defaults to 2048.

        Returns:
            tuple: frequency power (1D), phase (1D) and frequency (1D)
        """
        phases = []
        freqs = []
        for i in range(len(mix_signal)//CHIRP_LENGTH):
            start_, end_ = CHIRP_LENGTH*i, CHIRP_LENGTH*(i+1)
            mix_ = mix_signal[start_:end_]
            yf_ = rfft(mix_, CHIRP_LENGTH + window)
            phase_ = np.angle(yf_)
            phases.append(phase_)
            freqs.append(yf_)
        xf = rfftfreq(CHIRP_LENGTH + window, 1 / SAMPLE_RATE)
        phases = np.array(phases)
        freqs = np.array(freqs)
        return freqs, phases, xf

    def preprocess(self, signals:np.ndarray) -> tuple:
        """Extract distance and frequency

        Args:
            signals (np.ndarray): shape = (number of channels, number of samples)

        Returns:
            tuple: freqs_channel: 3-D array, shape = (number of channels, number of chirps, number of distance bins),
            xf: frequency that is used to convert to distance
        """
        # filter out frequencies beyond F0 and F0 + B
        signals = np.apply_along_axis(lambda x: butter_bandpass_filter(x, F0, F0 + B, SAMPLE_RATE), axis=1, arr=signals)
        
        # find where transmitted signals start, from that find start and end time of subsequent chirps
        y = np.correlate(signals[0], self.chirp[:CHIRP_LENGTH], 'valid')
        peaks, _ = signal.find_peaks(y, distance=CHIRP_LENGTH-50)

        peaks = np.array([peaks[5]])
        while peaks[-1] + CHIRP_LENGTH <= signals.shape[1]:
            peaks = np.append(peaks, peaks[-1] + CHIRP_LENGTH)

        # for each channel: for each chirp, mix with the transmitted chirp
        mix_signals = []
        for channel in range(signals.shape[0]):
            mix_signals.append(self.mix_operate(peaks, signals[channel]))

        # for each channel: use the mix chirp to get distance by time
        freqs_channel = []
        phases_channel = []
        for channel in range(signals.shape[0]):
            freqs, phases, xf = self.get_freqs_phases(mix_signals[channel])
            freqs_channel.append(freqs)
            phases_channel.append(phases)
        freqs_channel = np.array(freqs_channel)
        
        return freqs_channel, phases_channel, xf


    def extract_heart_rate(self, distance_time_specs: np.ndarray, distance_freq: np.ndarray,
                           min_distance:float, max_distance:float,
                           from_time:int, to_time:int,
                           gradient:bool=True,
                           freq_range:List[float]=[0.8,2.5]) -> tuple:
        """Extract heart rate and its corresponding distance

        Args:
            records_3d (np.ndarray): shape = (number of channels, number of chirps, number of distance bins)
            distance_freq (np.ndarray): 1D array. list of frequencies that are corresponding to distance
            min_distance (float): min distance of interest
            max_distance (float): max distance of interest
            from_time (int): from frame
            to_time (int): to frame
            gradient (bool, optional): Take gradient of the data or not. Defaults to True.
            freq_range (np.ndarray): frequency range. heart rate is from 0.8 to 2.5

        Returns:
            tuple: specs_channel: 2D array, shape = (number of channel, number of distance bins, number of heart rate frequency bins)
            hr_freq: 1D array, heart rate frequency
        """

        
        def get_freq_bin(data,freq_range, gradient=False):
            def smooth_radar_reflection(data):
                window = signal.hamming(len(data))
                data = data*window
                return data

            data = np.abs(data)
            if gradient:
                data = np.gradient(data,2)
                
            # padding to increase frequency resolution
            padding = len(data) + 2048
            data = smooth_radar_reflection(data)

            yf_ = rfft(data, padding)
            xf_ = rfftfreq(padding, 1/SR)
            yf_ = np.abs(yf_)
            
            lower_ = int(float(freq_range[0])/xf_[1])
            higher_ = int(float(freq_range[1])/xf_[1])
            yf_ = yf_[lower_:higher_]
            return yf_
        
        def get_xf(data_len, freq_range, window=2048):
            padding = data_len + window
            xf_ = rfftfreq(padding, 1/SR)
            lower_ = int(float(freq_range[0])/xf_[1])
            higher_ = int(float(freq_range[1])/xf_[1])
            return xf_[lower_:higher_]

        dist_min_bin = int(dist_to_freq(min_distance)/distance_freq[1]) 
        dist_max_bin = int(dist_to_freq(max_distance)/distance_freq[1])
        
        
        specs_channel = [np.apply_along_axis(lambda x: get_freq_bin(x,freq_range=freq_range,gradient=gradient),
                                             arr=distance_time_specs[channel,from_time:to_time,:],axis=0)[:,dist_min_bin:dist_max_bin].T for channel in range(NO_CHANNEL)]
        specs_channel = np.array(specs_channel)
        hr_freq = get_xf(distance_time_specs.shape[1],freq_range)
        
        return specs_channel, hr_freq
