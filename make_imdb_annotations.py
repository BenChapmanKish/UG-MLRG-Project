#!/usr/bin/python
# Ben Chapman-Kish
# 2016-07-22
# This script makes those annoying PASCAL annotations
# that py-faster-rcnn uses for its training image database

import os, sys, time, datetime
from PIL import Image

class ImgFace(object):
	def __init__(self, imgpath, annotpath, width, height):
		self.ip = imgpath
		self.ap = annotpath
		self.w = width
		self.h = height
		self.faces = []
		self.n = 0
	def add_face(self, x, y, w, h):
		self.faces.append((x, y, x+w, y+h))
		self.n += 1

with open(os.path.expanduser('~/aflw/frp.txt')) as f:
	facedata = [x.split() for x in f.readlines()]

#thispath = os.path.dirname(os.path.realpath(__file__))
imgdir = os.path.expanduser('~/caffe-model-project/AFLW_Faster_RCNN/data/Images/')
annotdir = os.path.expanduser('~/caffe-model-project/AFLW_Faster_RCNN/data/Annotations/')

imgind = []
imgface = {}

nfaces=len(facedata)
for i in range(nfaces):
	oimgp=facedata[i][1][2:]
	imgind.append(oimgp)
	if not imgface.has_key(oimgp):
		imgpath = imgdir + oimgp
		annotpath = annotdir + oimgp[:oimgp.index('.')] + '.txt'
		im=Image.open(imgpath)
		imgface[oimgp] = ImgFace(imgpath, annotpath, *im.size)
	sys.stdout.write('Processed face \033[33m'+str(i+1)+' / '+str(nfaces)+'\033[0m of file \033[1;34m'+str(oimgp)+'\033[0m\n')
	imgface[oimgp].add_face(*map(int, facedata[i][2:6]))

nimages=len(imgind)
for i in range(nimages):
	imf=imgface[imgind[i]]
	annot_text = '''\
# PASCAL Annotation Version 1.00

Image filename : "{}"
Image size (X x Y x C) : {:d} x {:d} x 3
Database : "The Annotated Facial Landmarks in the Wild database"
Objects with ground truth : {:d} {{ {} }}

# Top left pixel co-ordinates : (0, 0)

'''.format(imf.ip, imf.w, imf.h, imf.n, ' '.join(['"PASface"'] * imf.n))
	
	sys.stdout.write('\nProcessing image \033[35m'+str(imf.ip)+'\033[0m\n')
	for n in range(imf.n):
		sys.stdout.write('Face in coordinates \033[34m({:d}, {:d}, {:d}, {:d})\033[0m\n'.format(*imf.faces[n]))
		annot_text += '''# Details for object {num} ("PASface")
Original label for object {num} "PASface" : "face"
Bounding box for object {num} "PASface" (Xmin, Ymin) - (Xmax, Ymax) : ({:d}, {:d}) - ({:d}, {:d})

'''.format(num=n+1, *imf.faces[n])
	
	try:
		with open(imf.ap, 'w') as f:
			f.write(annot_text)
		sys.stdout.write('Annotations written to \033[32m'+str(imf.ap)+' \033[36m('+str(i+1)+' / '+str(nimages)+')\033[0m\n')
	except IOError:
		sys.stdout.write('\033[41mError writing annotations to '+str(imf.ap)+'...\033[0m\n')
		raw_input()

