import numpy as np
from scipy.signal import chirp
from scipy.io.wavfile import write
from config import *
import os
import logging
logging.basicConfig(format="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M", level=logging.DEBUG)


AMPLITUDE_CHIRP = 4000
REPEAT = int(5*60/T) # the generated chirps will last 5 minutes
CHIRP_FILE = 'data/{}_{}_{}_{}.wav'.format(AMPLITUDE_CHIRP, F0, F0+B, int(T*1000))
if __name__ == '__main__':
    """Generate chirp signal with params from the config file
    """
    t = np.linspace(0, T, CHIRP_LENGTH)
    waves = chirp(t, f0=F0, f1=F0+B, t1=T, method='linear') * AMPLITUDE_CHIRP
    waves = np.tile(waves, REPEAT)
    try:
        if not os.path.exists('data'):
            os.makedirs('data')
            
        write(CHIRP_FILE, SAMPLE_RATE, waves.astype(np.int16))
        logging.info(f'Save chirp file at {CHIRP_FILE}')
    except Exception as e:
        logging.error(e)
    
    