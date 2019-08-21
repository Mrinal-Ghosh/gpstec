"""
fits curve of sliced magnetic lat data to quantize MLT
"""

import cartomap as cm
import h5py
import numpy as np
from scipy import optimize, stats
import math
import matplotlib.pyplot as plt


def norm_fit(x, mu, sigma, a, b):
    return a * stats.norm.pdf(x, mu, sigma) + b


def sin_fit(x, a, b, c):
    return a * np.sin(b * x) + c


if __name__ == '__main__':
    fn = 'C:\\Users\\mrina\\Desktop\\data\\conv_0428T0000-0429T0000.h5'
    with h5py.File(fn, 'r') as f:
        lat = f['GPSTEC']['lat']
        lon = f['GPSTEC']['lon']
        t = f['GPSTEC']['time']
        im = f['GPSTEC']['im']

        _, _, x_ax, sl = cm.plotSlice(im=im, t=t, time=30, latline=50, magnetic=True, conjugate=True, average=True)
        par, par_cov = optimize.curve_fit(norm_fit, x_ax, sl)
        plt.plot(x_ax, norm_fit(x_ax, *par))
        # plt.legend(title='Best fit line')
        plt.show()
        print('Mean is {0:.2f}, s.d. is {1:.2f}'.format(par[0], par[1]))

