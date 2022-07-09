import numpy as np
import matplotlib
matplotlib.use("QT5AGG")
import pylab as pl
from scipy.ndimage import gaussian_filter1d

x_pixels = 512
y_pixels = 512
turnaround_pixels = 20
pixel_to_galvo_factor = 0.006

# Create the waveform
x_line = np.arange(0, x_pixels + turnaround_pixels*2, 1.0)

x = []
y = []
for i in range(y_pixels):
    if i % 2 == 0:
        x.extend(x_line)
    else:
        x.extend(x_line[::-1])
    y.extend(np.ones(x_pixels + turnaround_pixels*2, dtype=np.float) * i)

# Make all the dynamics slower, to help our poor galvos

# Concatenate to also take care of the jumps between frames
dx = np.diff(np.r_[x, x, x])
dy = np.diff(np.r_[y, y, y])

# low-pass filter the velocities
dx = gaussian_filter1d(dx, sigma=5)
dy = gaussian_filter1d(dy, sigma=5)

# Undo the concatenation
x = np.cumsum(dx)[len(x):len(x) * 2]
y = np.cumsum(dy)[len(x):len(x) * 2]

# The voltage of the galvos is simply a facotor times the mean-centered pixel location
Vx = (x - np.mean(x)) * pixel_to_galvo_factor
Vy = (y - np.mean(y)) * pixel_to_galvo_factor

# Round the pixel locations to be able to later use it as indices to place in the image
x = np.round(x).astype(np.uint16)
y = np.round(y).astype(np.uint16)

pl.plot(Vx, Vy)
pl.figure()
pl.plot(x, y)
pl.show()
