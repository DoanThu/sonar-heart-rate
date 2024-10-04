SAMPLE_RATE = 48000 # sample rate of the audio file
T = 0.02 # sweep time (s)
B = 5000 # bandwidth (Hz)
F0 = 15000 # initial frequency (Hz)
CHIRP_LENGTH = int(T*SAMPLE_RATE) # length of chirp counted in samples

NO_CHANNEL = 7 # no. channel of the microphone
C = 343 # speed of sound (m/s)
SR = int(1/T) # sample rate of the heart rate signal