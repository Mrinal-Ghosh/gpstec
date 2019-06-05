#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 15:24:36 2019

@author: smrak
"""

from glob import glob
import os
from gpstec import gpstec
from datetime import datetime
from dateutil import parser
import subprocess
from argparse import ArgumentParser

months = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10,
          'nov': 11, 'dec': 12}


def convert(root: str = None,
            date: str = None,
            tlim: str = None,
            ofn: str = None,
            force: bool = False):

    if os.path.splitext(root)[1] in ['.h5', '.hdf5']:  # FILE
        fn = root
        folder = os.path.split(fn)[0]

        if date is not None:
            datedt = parser.parse(date)
            dateday = datedt.strftime('%j')
        else:
            datedt = datetime.strptime(os.path.split(root)[1][3:9], '%y%m%d')
            dateday = datedt.strftime('%j')

        if tlim is None:
            if (int(dateday) + 1) > 365:
                year1 = int(datedt.year) + 1
                day1 = 1
            else:
                year1 = int(datedt.year)
                day1 = int(dateday) + 1
            tlim = [datetime.strptime("{} {}".format(str(datedt.year), str(dateday)), "%Y %j"),
                    datetime.strptime("{} {}".format(str(year1), str(day1)), "%Y %j")]
        else:
            tlim = parser.parse(tlim)

        if ofn is None:
            ofn = folder
        if os.path.isdir(ofn):
            ofn = os.path.join(ofn,
                               'conv_' + tlim[0].strftime('%m%dT%H%M') + '-' + tlim[1].strftime('%m%dT%H%M') + '.h5')

        if os.path.isfile(ofn):
            if not os.path.splitext(ofn)[1] in ['.h5', '.hdf5']:
                ofn = os.path.splitext(ofn)[0] + '.h5'

        if not os.path.exists(folder):
            subprocess.call('mkdir -p {}'.format(folder + '/'), shell=True, timeout=5)

        if os.path.exists(ofn) and not force:
            print('File already exists')
        else:
            print('Loading and rearranging data ...')
            D = gpstec.returnGlobalTEC(datafolder=fn, timelim=tlim)
            print('Saving data to ... {}'.format(ofn))
            gpstec.save2HDF(D['time'], D['xgrid'], D['ygrid'], D['tecim'], ofn)

    else:  # FOLDER
        flist = sorted(glob(os.path.split(root)[0] + '\\gps*.hdf5'))
        if len(flist) > 0:
            for file in flist:
                fn = file
                folder = os.path.split(fn)[0]

                datedt = datetime.strptime(os.path.split(fn)[1][3:9], '%y%m%d')
                dateday = datedt.strftime('%j')

                if tlim is None:
                    if (int(dateday) + 1) > 365:
                        year1 = int(datedt.year) + 1
                        day1 = 1
                    else:
                        year1 = int(datedt.year)
                        day1 = int(dateday) + 1
                    tlim = [datetime.strptime("{} {}".format(str(datedt.year), str(dateday)), "%Y %j"),
                            datetime.strptime("{} {}".format(str(year1), str(day1)), "%Y %j")]
                else:
                    tlim = parser.parse(tlim)

                if ofn is None:
                    ofn = folder
                if os.path.isdir(ofn):
                    ofn = os.path.join(ofn,
                                       'conv_' + tlim[0].strftime('%m%dT%H%M') + '-' + tlim[1].strftime(
                                           '%m%dT%H%M') + '.h5')

                if os.path.isfile(ofn):
                    if not os.path.splitext(ofn)[1] in ['.h5', '.hdf5']:
                        ofn = os.path.splitext(ofn)[0] + '.h5'

                if not os.path.exists(folder):
                    subprocess.call('mkdir -p {}'.format(folder + '/'), shell=True, timeout=5)

                if os.path.exists(ofn) and not force:
                    print('File already exists')
                else:
                    print('Loading and rearranging data ...')
                    D = gpstec.returnGlobalTEC(datafolder=fn, timelim=tlim)
                    print('Saving data to ... {}'.format(ofn))
                    gpstec.save2HDF(D['time'], D['xgrid'], D['ygrid'], D['tecim'], ofn)

                tlim = None
                ofn = None


if __name__ == '__main__':
    
    p = ArgumentParser()
    
    p.add_argument('root', type=str, help='local address')  # expected file
    p.add_argument('-d', '--date', type=str, help='date in YYYY-mm-dd format')
    p.add_argument('-o', '--ofn', help='Destination folder, if None-> the same as input folder', default=None)
    p.add_argument('--tlim', help='set time limits for the file to convert', nargs=2)
    p.add_argument('--force', help='Do you want to override existing files?', action='store_true')

    P = p.parse_args()
    
    convert(root=P.root, date=P.date, tlim=P.tlim, ofn=P.ofn, force=P.force)
