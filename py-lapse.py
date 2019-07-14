#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import os
from argparse import ArgumentParser
import numpy as np


def lapse(root: str = None,
          width: int = None,
          height: int = None,
          fps: float = None,
          name: str = None,
          gamma: float = None):
    """convert sequential png files to mp4"""

    if os.path.split(root)[1] == '':
        folder = os.path.join(root)[0]
    else:
        folder = root

    invgamma = 1 / gamma
    table = np.array([((i / 255.0) ** invgamma) * 255 for i in np.arange(0, 256)]).astype('uint8')

    fourcc = 0x7634706d
    images = [img for img in os.listdir(folder) if img.endswith('.png')]
    frame = cv2.imread(os.path.join(folder, images[0]))

    if height is None or width is None:
        height, width, layers = frame.shape
    if name is None:
        name = os.path.join(folder, '{}.mp4'.format(os.path.split(folder)[1]))
        print(name)
    if fps is None:
        fps = len(images)/15

    video = cv2.VideoWriter(name, fourcc, fps, (width, height))

    for image in images:
        im = cv2.imread(os.path.join(folder, image))
        res = cv2.resize(cv2.LUT(im, table), (width, height), interpolation=cv2.INTER_AREA)
        video.write(res)

    cv2.destroyAllWindows()
    video.release()


if __name__ == '__main__':
    p = ArgumentParser()
    p.add_argument('root', type=str, help='folder containing images')
    p.add_argument('-w', '--width', type=int, help='width in pixels', default=None)
    p.add_argument('-l', '--height', type=int, help='height in pixels', default=None)
    p.add_argument('-f', '--fps', type=float, help='frames per second', default=None)
    p.add_argument('-n', '--name', type=str, help='output name with .mp4 ext', default=None)
    p.add_argument('-g', '--gamma', type=float, default=1.4)

    P = p.parse_args()

    lapse(root=P.root, width=P.width, height=P.height, fps=P.fps, name=P.name, gamma=P.gamma)
