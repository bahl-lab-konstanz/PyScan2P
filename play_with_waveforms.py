import numpy as np
import numpy as np
import matplotlib
matplotlib.use("MacOSX")
import pylab as pl
from scipy.ndimage import gaussian_filter1d, convolve1d
from numba import jit

@jit(nopython=True)
def do_binning(img_channel0, img_channel1, pmt_data_channel0, pmt_data_channel1, x, y, bin_size):

    for i in range(len(x)):
        for j in range(bin_size):
            img_channel0[round(y[i]), round(x[i])] += pmt_data_channel0[i * bin_size + j] / bin_size
            img_channel1[round(y[i]), round(x[i])] += pmt_data_channel1[i * bin_size + j] / bin_size


x_pixels = 500
y_pixels = 500

x_line = np.arange(0, x_pixels, 1.0)

x = []
y = []
for i in range(y_pixels):
    if i%2 == 0:
        x.extend(x_line)
    else:
        x.extend(x_line[::-1])
    y.extend(np.ones(x_pixels, dtype=np.float)*i)

pl.plot(x, y)

dx = np.diff(x)
dy = np.diff(y)

dx = gaussian_filter1d(dx, sigma=5)
dy = gaussian_filter1d(dy, sigma=5)

x = np.cumsum(dx)
y = np.cumsum(dy)

# x and y are the locations in your image!
pixel_to_galvo_factor = 0.002
vx = (x - np.mean(x))*pixel_to_galvo_factor
vy = (y - np.mean(y))*pixel_to_galvo_factor

# the input rate from the pmts, is higher!
bin_size = 5
output_rate = 500000
input_rate = output_rate*bin_size # Ma x 3.57 MhZ allowed!!!


# send this to galvos with a output rate


pl.plot(vx, vy)
pl.show()


pmt_channel0 = np.random.random(size=len(x)*bin_size)*20000 + 10000
pmt_channel1 = np.random.random(size=len(x)*bin_size)*20000 + 10000
img_channel0 = np.zeros((x_pixels, y_pixels), dtype=np.float64)
img_channel1 = np.zeros((x_pixels, y_pixels), dtype=np.float64)

do_binning(img_channel0, img_channel1, pmt_channel0, pmt_channel1, x, y, bin_size)

img_channel0 = img_channel0.astype(np.uint16)
img_channel1 = img_channel1.astype(np.uint16)

pl.imshow(img_channel0)
pl.show()


