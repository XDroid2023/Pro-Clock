import pygame
import numpy as np
import os
import wave
import struct

# Initialize pygame mixer
pygame.mixer.init(44100, -16, 1, 1024)

# Create a simple tick sound
sample_rate = 44100
duration = 0.05  # seconds
t = np.linspace(0, duration, int(sample_rate * duration))
frequency = 1000  # Hz
amplitude = 0.3

# Generate a sine wave with exponential decay
wave_data = amplitude * np.sin(2 * np.pi * frequency * t) * np.exp(-10 * t)
wave_data = (wave_data * 32767).astype(np.int16)

# Create directory if it doesn't exist
if not os.path.exists('sounds'):
    os.makedirs('sounds')

# Save the sound as WAV file
with wave.open('sounds/tick.wav', 'w') as wav_file:
    # Set parameters
    nchannels = 1
    sampwidth = 2
    nframes = len(wave_data)
    
    # Set WAV file parameters
    wav_file.setnchannels(nchannels)
    wav_file.setsampwidth(sampwidth)
    wav_file.setframerate(sample_rate)
    
    # Write the data
    for sample in wave_data:
        wav_file.writeframes(struct.pack('h', sample))
