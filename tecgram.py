#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 10:49 2019
adapted from scivision
author mrinalghosh
"""

from datetime import datetime
from matplotlib.pyplot import figure, show
import matplotlib.dates as mdates
import numpy as np
import h5py
from argparse import ArgumentParser
import multiprocessing
from itertools import repeat
from glob import glob
import os
from sys import platform
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()

# def test_plot2d_datetime():
#     t = np.arange('2010-05-04T12:05:00', '2010-05-04T12:05:01', dtype='datetime64[ms]')
#     y = np.random.randn(t.size)
#
#     # t = t.astype(datetime)  # Matplotlib < 2.2
#
#     ax = figure().gca()
#     ax.plot(t, y)


# def test_plot2d_xarray():
#     t = np.arange('2010-05-04T12:05:00', '2010-05-04T12:05:01', dtype='datetime64[ms]')
#     y = np.random.randn(t.size)
#
#     dat = xarray.DataArray(y, coords={'time': t}, dims=['time'])
#
#     dset = xarray.Dataset({'random1Dstuff': dat})
#
#     fg = figure()
#     ax = fg.subplots(3, 1, sharex=True)
#
#     dat.plot(ax=ax[0])
#
#     ax[1].plot(dat.time, dat)
#
#     dset['random1Dstuff'].plot(ax=ax[2])

def poolkeo(flist, latline, lonline):
    with multiprocessing.Pool() as pool:
        pool.starmap(keogram, zip(flist, repeat(latline), repeat(lonline)))


def keogram(fn: str = None,
            latline: int = None,
            lonline: int = None):

    # default
    def_lat = 41

    with h5py.File(fn,'r') as f:
        lat = f['GPSTEC']['lat']
        lon = f['GPSTEC']['lon']
        t = f['GPSTEC']['time']
        t = list(map(datetime.fromtimestamp, t))

        if latline is None:
            im = np.array(f['GPSTEC']['im'])[0:, lonline, 0:]
            y = range(-90, 89)
        elif lonline is None:
            im = np.array(f['GPSTEC']['im'])[0:, 0:, latline]
            y = range(-180, 179)
        else:
            im = np.array(f['GPSTEC']['im'])[0:, 0:, def_lat]
            y = range(-180, 179)

        im = np.flipud(np.transpose(im))
        print(im.shape)
        mt = mdates.date2num((t[0], t[-1]))

        fig = figure()
        ax = fig.gca()
        fig.suptitle(f'{t[0].strftime("%Y-%m-%d")}')

        ax.imshow(im, extent=[mt[0], mt[1], y[0], y[-1]], aspect='auto')

        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        fig.autofmt_xdate()

        show()


if __name__ == '__main__':
    p = ArgumentParser()
    p.add_argument('root', type=str,  help='local folder or file')
    p.add_argument('-t', '--latline', type=int, help='latitude value [-90,89]')
    p.add_argument('-n', '--lonline', type=int, help='longitude value [-180,179]')

    P = p.parse_args()
    root = P.root

    if os.path.splitext(root)[1] in ['.h5', '.hdf5']:
        flist = [root]
    else:
        if platform == 'win32':
            if len(os.path.split(root)[1]) == 0:  # cases for trailing backslash
                flist = sorted(glob(os.path.split(root)[0] + '\\conv*.h5'))
            else:
                flist = sorted(glob(root + '\\conv*.h5'))
        elif platform in ['linux', 'linux2']:
            if len(os.path.split(root)[1]) == 0:
                flist = sorted(glob(os.path.split(root)[0] + '/conv*.h5'))
            else:
                flist = sorted(glob(root + '/conv*.h5'))

    if len(flist) > 0:
        # print(flist)
        poolkeo(flist, latline=P.latline, lonline=P.lonline)
