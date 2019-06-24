#!/usr/bin/env python

import matplotlib.pyplot as plt
import cartomap as cm
import numpy as np
import cartopy.crs as ccrs
import h5py
from argparse import ArgumentParser
from datetime import datetime
import os
from glob import glob
from sys import platform

months = {1: 'jan', 2: 'feb', 3: 'mar', 4: 'apr', 5: 'may', 6: 'jun',
          7: 'jul', 8: 'aug', 9: 'sep', 10: 'oct', 11: 'nov', 12: 'dec'}

projections = {'plate': [ccrs.PlateCarree(), 'Plate Carree'],
               'near': [ccrs.NearsidePerspective(), 'Nearside Perspective'],
               'northpole': [ccrs.NorthPolarStereo(), 'North Polar Stereo'],
               'southpole': [ccrs.SouthPolarStereo(), 'South Polar Stereo'],
               'mercator': [ccrs.Mercator(), 'Mercator'],
               'geostat': [ccrs.Geostationary(), 'Geostationary']}

cmaps = plt.colormaps()


def save(root: str = None,
         n: int = None,
         overlap: bool = False,
         slide: str = None,
         proj: str = None,
         lim: float = None,
         cmap: str = None):

    f = h5py.File(root, 'r')
    lat = f['GPSTEC']['lat']
    lon = f['GPSTEC']['lon']
    t = f['GPSTEC']['time']

    if cmap not in cmaps:
        cmap = 'gist_ncar'

    if slide is not None:
        slide = int(slide)
        if slide+n-1 <= len(t):
            im = np.nanmean(f['GPSTEC']['im'][0:][0:][slide:slide+n+1], axis=0)
        im = np.transpose(im)
        time = datetime.fromtimestamp(t[slide])

        # scale cmap
        cmax = np.max(list(filter(lambda x: ~np.isnan(x), np.reshape(im, 64800))))
        cmin = np.min(list(filter(lambda x: ~np.isnan(x), np.reshape(im, 64800))))
        minoff = 0  # offset
        maxoff = 0

        fig, ax = cm.plotCartoMap(projection=proj, terrain=True)
        msh = ax.pcolormesh(lon, lat, im, transform=ccrs.PlateCarree(), vmin=cmin + minoff, vmax=cmax - maxoff,
                            cmap=cmap)
        cbar_ax = fig.add_axes([0.85, 0.15, 0.02, 0.7])
        fig.colorbar(msh, cax=cbar_ax, label='Total Electron Concentration [TECu]')

        print('Saving slide {}'.format(slide))

        if platform == 'win32':
            os.mkdir(os.path.split(root)[0] + '\\{}{}'.format(months[time.month], time.day))
        elif platform in ['linux', 'linux2']:
            os.mkdir(os.path.split(root)[0] + '/{}{}'.format(months[time.month], time.day))

        folder = os.path.join(os.path.split(root)[0], '{}{}'.format(months[time.month], time.day))
        print(folder)

        figsav = plt.gcf()
        figsav.suptitle('{}'.format(time))
        figsav.set_size_inches((10, 5), forward=False)
        figsav.savefig(os.path.join(folder, '{}.png'.format(str(slide).zfill(3))), dpi=200)
        plt.close(fig)
        plt.close(figsav)
    else:
        t0 = datetime.fromtimestamp(t[0])

        if platform == 'win32':
            os.mkdir(os.path.split(root)[0] + '\\{}{}'.format(months[t0.month], t0.day))
        elif platform in ['linux', 'linux2']:
            os.mkdir(os.path.split(root)[0] + '/{}{}'.format(months[t0.month], t0.day))
        folder = os.path.join(os.path.split(root)[0], '{}{}'.format(months[t0.month], t0.day))

        if not overlap:
            slides = list(map(lambda x: x*n, list(range(int(len(t)/n)-1))))
        else:
            slides = list(range(len(t)-n+1))

        for slide in slides:
            time = datetime.fromtimestamp(t[slide])
            if lim is not 0:
                cmax = lim
                cmin = 0.0
            else:
                cmax = np.max(list(filter(lambda x: ~np.isnan(x), np.reshape(im, 64800))))
                cmin = np.min(list(filter(lambda x: ~np.isnan(x), np.reshape(im, 64800))))

            im = np.nanmean(f['GPSTEC']['im'][0:][0:][slide:slide+n+1], axis=0)
            im = np.transpose(im)

            fig, ax = cm.plotCartoMap(projection=proj, terrain=True)
            msh = ax.pcolormesh(lon, lat, im, transform=ccrs.PlateCarree(), vmin=cmin, vmax=cmax, cmap=cmap)
            cbar_ax = fig.add_axes([0.85, 0.15, 0.02, 0.7])
            fig.colorbar(msh, cax=cbar_ax, label='Total Electron Concentration [TECu]')

            print('Saving slide {}/{}...'.format(slide+1, len(t)))
            figsav = plt.gcf()
            figsav.suptitle('{}'.format(time))
            figsav.set_size_inches((10, 5), forward=False)
            figsav.savefig(os.path.join(folder, '{}.png'.format(str(slide).zfill(3))), dpi=200)
            plt.close(fig)
            plt.close(figsav)

        print(folder)


if __name__ == '__main__':
    p = ArgumentParser()
    p.add_argument('root', type=str, help='local address')
    p.add_argument('-n', '--naverage', type=int, help='number of slides to include in average', default=1)
    p.add_argument('--overlap', help='allow overlap of slides', action='store_true')
    p.add_argument('-s', '--slide', type=str, help='slide number [0,239]')
    p.add_argument('-p', '--proj', type=str, help='map projection - northpole, southpole, plate etc.', default='northpole')
    p.add_argument('-l', '--lim', type=float, help='absolute limit of colorbar - 0 for no absolute', default=70)
    p.add_argument('-c', '--cmap', type=str, help='colormap', default=None)

    P = p.parse_args()

    root = P.root

    if os.path.splitext(root)[1] in ['.h5', '.hdf5']:
        save(root=P.root, n=P.naverage, overlap=P.overlap, slide=P.slide, proj=P.proj, lim=P.lim, cmap=P.cmap)

    else:
        if platform == 'win32':
            flist = sorted(glob(os.path.split(root)[0] + '\\conv*.h5'))
        elif platform in ['linux', 'linux2']:
            flist = sorted(glob(os.path.split(root)[0] + '/conv*.h5'))

        if len(flist) > 0:
            for file in flist:
                save(file, n=P.naverage, overlap=P.overlap, slide=P.slide, proj=P.proj, lim=P.lim, cmap=P.cmap)

