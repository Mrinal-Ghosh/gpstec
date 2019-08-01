#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 10:49 2019
adapted from scivision
author mrinalghosh
"""

from datetime import datetime
import matplotlib.pyplot as plt
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
from apexpy import Apex

register_matplotlib_converters()

# use the plotKeogram function of CartoMap instead

def poolkeo(flist, latline, lonline, odir, apex, geo):
    with multiprocessing.Pool() as pool:
        pool.starmap(keogram, zip(flist, repeat(latline), repeat(lonline), repeat(odir), repeat(apex), repeat(geo)))


def keogram(fn=None, latline=None, lonline=None, odir=None, apex=False, geo=False):

    mlon_levels = list(range(-180, 180, 20))
    mlat_levels = list(range(-90, 90, 10))
    glon_levels = list(range(-180, 180, 20))
    glat_levels = list(range(-90, 90, 10))
    height=350

    with h5py.File(fn, 'r') as f:
        lat = f['GPSTEC']['lat']
        lon = f['GPSTEC']['lon']
        t = f['GPSTEC']['time']
        t = list(map(datetime.fromtimestamp, t))
        A = Apex(date=t[0])

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
        mt = mdates.date2num((t[0], t[-1]))

        fig = plt.figure()
        ax = fig.gca()
        fig.suptitle(f'{t[0].strftime("%Y-%m-%d")}')

        ax.imshow(im, extent=[mt[0], mt[1], y[0], y[-1]], aspect='auto')

        if latline is None:
            if apex is True:
                for level in mlat_levels:
                    glat, _ = A.convert(level, lonline, 'geo', 'apex', height=height)
                    ax.axhline(glat, linestyle='--', linewidth=1, color='firebrick')
                    # print(f'{level} in geo is {glat} in apex')
            if geo is True:
                for level in glat_levels:
                    ax.axhline(level, linestyle='--', linewidth=1, color='cornflowerblue')
        elif lonline is None:
            if apex is True:
                for level in mlon_levels:
                    _, glon = A.convert(latline, level, 'geo', 'apex', height=height)
                    ax.axhline(glon, linestyle='--', linewidth=1, color='firebrick')
                    # print(f'{level} in geo is {glon} in apex')
            if geo is True:
                for level in glon_levels:
                    ax.axhline(level, linestyle='--', linewidth=1, color='cornflowerblue')

        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        fig.autofmt_xdate()

        if odir != '-':
            fig.savefig(os.path.join(odir, '{}.png'.format(mt[0])), dpi=200)
        else:
            plt.show()


if __name__ == '__main__':
    p = ArgumentParser()
    p.add_argument('root', type=str,  help='local folder or file')
    p.add_argument('-t', '--latline', type=int, help='latitude value [-90,89]')
    p.add_argument('-n', '--lonline', type=int, help='longitude value [-180,179]')
    p.add_argument('-o', '--odir', type=str, help='save images to directory', default='-')
    p.add_argument('--apex', help='apex coordinates', action='store_true')
    p.add_argument('--geo', help='geo coordinates', action='store_true')

    P = p.parse_args()
    root = P.root

    if os.path.splitext(root)[1] in ['.h5', '.hdf5']:
        keogram(root, P.latline, P.lonline, P.odir, P.apex, P.geo)
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
            poolkeo(flist, latline=P.latline, lonline=P.lonline, odir=P.odir, apex=P.apex, geo=P.geo)
