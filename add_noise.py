#!/usr/bin/python
# Ben Chapman-Kish
# 2016-07-14
import matplotlib.pyplot as plt
import sys, skimage, skimage.viewer

imname=sys.argv[1]
image = skimage.io.imread(imname)
noise_image = skimage.util.random_noise(image, mode='poisson') # or gaussian
viewer=skimage.viewer.ImageViewer(noise_image)
viewer.show()
skimage.io.imsave(imname[:imname.index('.')]+'-new.jpg', noise_image)
