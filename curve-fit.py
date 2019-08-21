"""
normally fits curve of sliced magnetic lat data to quantize MLT
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
    """
    does not create stable graphs
    """
    return a * np.sin(b * x) + c


if __name__ == '__main__':
    fn = 'C:\\Users\\mrina\\Desktop\\data\\conv_0428T0000-0429T0000.h5'
    with h5py.File(fn, 'r') as f:
        # lat = f['GPSTEC']['lat']
        # lon = f['GPSTEC']['lon']
        t = f['GPSTEC']['time']
        im = f['GPSTEC']['im']

        # latitudes = list(range(-90,90))
        # for lat in latitudes:
        #     try:
        #         _, _, x_ax, sl = cm.plotSlice(im=im, t=t, time=0, latline=lat,
        #                                       magnetic=True, conjugate=True, average=True)
        #         par, par_cov = optimize.curve_fit(norm_fit, x_ax, sl)
        #         # plt.plot(x_ax, norm_fit(x_ax, *par))
        #         plt.close()
        #         # plt.show()
        #         print('At {0:d}, mean is {1:.2f}, s.d. is {2:.2f}'.format(lat, par[0], par[1]))
        #     except:
        #         print('Not enough data points to optimize')

        lat = 30
        _, _, x_ax, sl = cm.plotSlice(im=im, t=t, time=0, latline=lat, magnetic=True, conjugate=False, average=True)
        par, par_cov = optimize.curve_fit(norm_fit, x_ax, sl)
        plt.plot(x_ax, norm_fit(x_ax, *par))
        # plt.close()
        plt.show()
        print('At latitude {0:d}, mean is longitude {1:.2f}, s.d. is {2:.2f}'.format(lat, par[0], par[1]))
