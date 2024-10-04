import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.fft import rfft, rfftfreq, fft, fftfreq, ifft
from scipy.ndimage import gaussian_filter
from config import *


def sort_peaks(peaks, y, descending=True):
    t = [y[peak] for peak in peaks]
    temp = np.argsort(t)
    if descending:
        temp = temp[::-1]
    peaks_sorted = [peaks[i] for i in temp]
    return peaks_sorted


def write_to_file(file_name, data):
    with open(file_name, 'w') as f:
        f.write(data)


def get_yf_xf(signal, sample_rate, window=0, r_fft=True):
    if r_fft:
        yf = rfft(signal)
        xf = rfftfreq(len(signal)+window, 1 / sample_rate)
    else:
        yf = fft(signal)
        xf = fftfreq(len(signal)+window, 1 / sample_rate)
    return yf, xf


def smooth_signal(x, window_size=13, order=3):
    return savgol_filter(x, window_size, order)


def smooth(x, window_len=12, window='hanning'):
    # https://scipy-cookbook.readthedocs.io/items/SignalSmooth.html
    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")
    if window_len<3:
        return x
    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")
    s = np.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
    if window == 'flat': # moving average
        w = np.ones(window_len,'d')
    else:
        w = eval('np.'+window+'(window_len)')

    y = np.convolve(w/w.sum(), s, mode='valid')
    # return y
    return y[(window_len//2-1):-(window_len//2)]


def gaussian_blur(stack_spec,sigma=1,order=0):
    intensity_smooth = gaussian_filter(stack_spec, sigma=sigma, order=order)
    return intensity_smooth


def dist_to_freq(dist):
    return dist*2/C*B/T

def freq_to_dist(freq):
    return freq*T/B*C/2