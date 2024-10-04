import librosa
import matplotlib.pyplot as plt
import numpy as np

def plot_frequency_time(data: np.ndarray, sample_rate:int, title='Spectrogram', n_fft=2048):
    """Plot spectrogram of audio signal

    Args:
        data (np.ndarray): audio signal and is 1-D array
        sample_rate (int): sample rate of the audio signal
        title (str, optional): title of the spectrogram. Defaults to 'Spectrogram'.
        n_fft (int, optional): length of the window signal. Defaults to 2048. More info in:
        https://librosa.org/doc/main/generated/librosa.stft.html 
    """
    X = librosa.stft(data, n_fft=n_fft)
    Xdb = librosa.amplitude_to_db(abs(X))
    plt.figure(figsize=(14, 5))
    librosa.display.specshow(Xdb, sr=sample_rate, x_axis='time', y_axis='hz')
    plt.colorbar()
    plt.title(title)
    plt.show()
    
